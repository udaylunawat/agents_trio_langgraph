import json, glob, os
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from utils import create_llm, get_health_implication

class AQIQuery(BaseModel):
    city: str = Field(..., description="City name in the AQI files")
    date: str = Field(..., description="ISO date like 2025-10-23")
    question: str = Field(..., description="User's natural-language question")
    llm_provider: str = Field(default="OpenRouter", description="LLM provider: OpenAI or OpenRouter")
    model_name: str = Field(default="minimax/minimax-m2:free", description="Model name to use")
    api_key: str = Field(..., description="API key for the selected provider")
    aqi_file: str = Field(None, description="AQI data as a JSON string")

def answer_aqi(payload: AQIQuery):
    if payload.aqi_file:
        # Load AQI data from the uploaded file content
        rec = json.loads(payload.aqi_file)
    else:
        # Load AQI data from local files
        files = glob.glob(os.path.join("data","aqi","*.json"))
        data = []
        for fp in files:
            with open(fp) as f:
                data.append(json.load(f))

        # Find matching record
        rec = next((r for r in data if r.get("city","").lower()==payload.city.lower() and r.get("date")==payload.date), None)
        if not rec:
            return {
                "answer": f"No AQI record found for {payload.city} on {payload.date}. Try available files.",
                "available": [os.path.basename(f) for f in files]
            }

    # Initialize LLM based on user selection
    llm = create_llm(payload.llm_provider, payload.model_name, payload.api_key)

    # Create prompt template
    prompt = PromptTemplate(
        input_variables=["city", "date", "aqi", "pm25", "pm10", "o3", "no2", "question"],
        template="""
You are an air quality expert. A user is asking about air quality in {city} on {date}.

Current air quality data:
- AQI: {aqi}
- PM2.5: {pm25} µg/m³
- PM10: {pm10} µg/m³
- Ozone (O3): {o3} µg/m³
- Nitrogen Dioxide (NO2): {no2} µg/m³

User question: {question}

Provide a helpful, natural language response that:
1. Explains the air quality levels and health implications
2. Answers their specific question
3. Gives relevant safety advice if needed
4. Keeps the response concise but informative

Response:"""
    )

    # Prepare data
    aqi_data = {
        "city": rec["city"],
        "date": rec["date"],
        "aqi": rec["aqi"],
        "pm25": rec["pm2_5"],
        "pm10": rec["pm10"],
        "o3": rec["o3"],
        "no2": rec["no2"],
        "question": payload.question
    }

    # Generate response
    try:
        response = llm.invoke(prompt.format(**aqi_data))
        answer = response.content.strip()
    except Exception as e:
        # Fallback to simple response if LLM fails
        aqi = rec["aqi"]
        cat = "Good" if aqi<=50 else "Moderate" if aqi<=100 else "Unhealthy for Sensitive" if aqi<=150 else "Unhealthy" if aqi<=200 else "Very Unhealthy" if aqi<=300 else "Hazardous"
        answer = f"{rec['city']} on {rec['date']}: AQI {aqi} ({cat}). This air quality level means: {get_health_implication(aqi)}. Key pollutants: pm2_5={rec['pm2_5']}, pm10={rec['pm10']}, o3={rec['o3']}, no2={rec['no2']}."

    return {
        "answer": answer,
        "record": rec
    }
