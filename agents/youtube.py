import os
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import create_llm_youtube

class YTRequest(BaseModel):
    prompt: str = Field(..., description="Describe what you want to make next")
    top_k: int = 3
    llm_provider: str = Field(default="OpenRouter", description="LLM provider: OpenAI or OpenRouter")
    model_name: str = Field(default="minimax/minimax-m2:free", description="Model name to use")
    api_key: str = Field(..., description="API key for the selected provider")

def recommend_next(payload: YTRequest, path="data/youtube.csv"):
    try:
        df = pd.read_csv(path)
        df["score"] = df["likes"]*2 + df["views"]/100
        corpus = df["script"].fillna("").tolist()
        vec = TfidfVectorizer(stop_words="english")
        X = vec.fit_transform(corpus + [payload.prompt])
        sims = cosine_similarity(X[-1], X[:-1]).ravel()
        df["similarity"] = sims
        # Weight by historic performance
        df["rank_score"] = 0.6*df["similarity"] + 0.4*( (df["score"] - df["score"].min())/(df["score"].max()-df["score"].min()+1e-6) )
        top = df.sort_values("rank_score", ascending=False).head(payload.top_k)

        # Initialize LLM based on user selection (higher temperature for creative tasks)
        llm = create_llm_youtube(payload.llm_provider, payload.model_name, payload.api_key)

        recs = []
        for _, r in top.iterrows():
            # Use LLM to generate creative title, hook, and outline
            prompt = PromptTemplate(
                input_variables=["user_prompt", "existing_title", "existing_script"],
                template="""
                You are a YouTube video strategist. A creator wants to make a video about: "{user_prompt}"

                They liked this existing video: "{existing_title}"
                Script snippet: "{existing_script}"

                Generate:
                1. A compelling video title (under 60 characters)
                2. A strong hook opening line
                3. A 5-step video script outline

                Make it engaging and likely to perform well. Focus on the angle that would appeal to their audience.

                Format as JSON with keys: title, hook, outline (as array of strings)
                """
            )

            response = llm.invoke(prompt.format(
                user_prompt=payload.prompt,
                existing_title=r["title"],
                existing_script=r["script"][:200] + "..." if len(r["script"]) > 200 else r["script"]
            ))

            # Parse LLM response - for simplicity, we'll create the structured response
            # In a real app, you'd parse the JSON from the LLM response
            title = f"Next: {payload.prompt.split()[0].title()} Unlocked - What You Need to Know"
            hook = f"Hook idea: What if {payload.prompt.split()[0]} was easier than you think?"

            outline = [
                "Hook: Start with a surprising statistic or question",
                "Show the problem: Demonstrate why this matters",
                "Present the solution: Step-by-step breakdown",
                "Real-world example: Show it in action",
                "Call to action: What viewers should do next"
            ]

            try:
                # Attempt to parse JSON from LLM response
                import json
                llm_data = json.loads(response.content.strip())
                if "title" in llm_data:
                    title = llm_data["title"]
                if "hook" in llm_data:
                    hook = llm_data["hook"]
                if "outline" in llm_data:
                    outline = llm_data["outline"]
            except:
                pass  # Use default if JSON parsing fails

            recs.append({
                "suggested_title": title,
                "hook": hook,
                "inspired_by": r["title"],
                "performance_score": f"likes={int(r['likes'])}, views={int(r['views'])}",
                "why_this_angle": f"Similar to your prompt '{payload.prompt}' with proven engagement metrics",
                "outline": outline
            })

        return {"recommendations": recs}

    except Exception as e:
        # Fallback to simple recommendations without LLM
        return {"error": f"YouTube recommendation failed: {str(e)}", "recommendations": []}
