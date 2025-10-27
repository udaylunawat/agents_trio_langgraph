import streamlit as st
import requests
import json

st.title("Micro Agents (AQI / PDFs / YouTube)")

# Sidebar for LLM configuration
st.sidebar.header("⚙️ LLM Configuration")

llm_provider = st.sidebar.selectbox(
    "Choose LLM Provider",
    ["OpenRouter", "OpenAI"],
    help="Select your preferred AI service"
)

if llm_provider == "OpenRouter":
    api_key = st.sidebar.text_input(
        "OpenRouter API Key",
        type="password",
        placeholder="ysk-or-v1-...",
        help="Get your key from https://openrouter.ai/keys"
    )
    model_name = st.sidebar.selectbox(
        "Model",
        ["minimax/minimax-m2:free", "anthropic/claude-3-haiku", "openai/gpt-4o-mini"],
        help="Choose your preferred model"
    )
else:  # OpenAI
    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Get your key from https://platform.openai.com/api-keys"
    )
    model_name = st.sidebar.selectbox(
        "Model",
        ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"],
        help="Choose your preferred model"
    )

# Validate API key input
if not api_key:
    st.sidebar.warning("⚠️ Please enter your API key")
else:
    st.sidebar.success("✅ API key configured")

# Create tabs for each agent
tab1, tab2, tab3 = st.tabs(["AQI Agent", "PDF Agent", "YouTube Agent"])

with tab1:
    st.header("AQI Agent")
    aqi_file = st.file_uploader("Upload AQI JSON", type="json")
    aqi_city = st.text_input("City", "Delhi", disabled=aqi_file is not None)
    aqi_date = st.text_input("Date (ISO format)", "2025-10-23", disabled=aqi_file is not None)
    aqi_question = st.text_input("Question", "Is it safe to run outside?")
    if st.button("Query AQI", key="aqi_button"):
        if not api_key:
            st.error("Please enter your API key in the sidebar")
        else:
            try:
                payload = {
                    "question": aqi_question,
                    "llm_provider": llm_provider,
                    "model_name": model_name,
                    "api_key": api_key,
                    "aqi_file": aqi_file.read().decode("utf-8") if aqi_file else None,  # Send JSON content if uploaded
                    "city": "" if aqi_file else aqi_city,
                    "date": "" if aqi_file else aqi_date
                }
                st.write("Payload being sent to backend:")
                st.write(payload)
                response = requests.post("http://localhost:8000/aqi/query", json=payload)
                result = response.json()
                st.write(result)
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the backend server. Please ensure the FastAPI server is running on port 8000.")
            except requests.exceptions.JSONDecodeError:
                st.error("Failed to receive valid response from server. Please check the API key and ensure the backend is running.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

with tab2:
    st.header("PDF Agent")
    pdf_file = st.file_uploader("Upload PDF", type="pdf")
    pdf_question = st.text_input("Question about PDFs", "What are agent workflows and how to evaluate them?")
    pdf_top_k = st.number_input("Top K results", min_value=1, max_value=10, value=2)
    if st.button("Query PDFs", key="pdf_button"):
        if not api_key:
            st.error("Please enter your API key in the sidebar")
        else:
            try:
                payload = {
                    "question": pdf_question,
                    "top_k": pdf_top_k,
                    "llm_provider": llm_provider,
                    "model_name": model_name,
                    "api_key": api_key,
                    "pdf_file": pdf_file.read().decode("latin-1", errors="ignore") if pdf_file else None  # Send PDF content if uploaded
                }
                response = requests.post("http://localhost:8000/pdfs/query", json=payload)
                result = response.json()
                st.write("**Answer:**")
                st.write(result.get("answer", "No answer provided"))

                if result.get("citations"):
                    st.write("**Sources:**")
                    for citation in result["citations"]:
                        with st.expander(f"Source {citation['rank']}: {citation['source']}"):
                            st.write(citation["content_preview"])
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the backend server. Please ensure the FastAPI server is running on port 8000.")
            except requests.exceptions.JSONDecodeError:
                st.error("Failed to receive valid response from server. Please check the API key and ensure the backend is running.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

with tab3:
    st.header("YouTube Agent")
    youtube_file = st.file_uploader("Upload YouTube CSV", type="csv")
    yt_prompt = st.text_input("Prompt for YouTube script", "I want a video about building agent workflows for PDFs")
    yt_top_k = st.number_input("Top K recommendations", min_value=1, max_value=10, value=3)
    if st.button("Recommend YouTube Script", key="yt_button"):
        if not api_key:
            st.error("Please enter your API key in the sidebar")
        else:
            try:
                payload = {
                    "prompt": yt_prompt,
                    "top_k": yt_top_k,
                    "llm_provider": llm_provider,
                    "model_name": model_name,
                    "api_key": api_key,
                    "youtube_file": youtube_file.read().decode("utf-8") if youtube_file else None,  # Send CSV content if uploaded
                    "youtube_file_present": youtube_file is not None
                }
                response = requests.post("http://localhost:8000/youtube/recommend", json=payload)
                result = response.json()
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.write("**Video Recommendations:**")
                    for rec in result.get("recommendations", []):
                        with st.expander(f"🎬 {rec.get('suggested_title', 'Untitled')}"):
                            st.write(f"**Hook:** {rec.get('hook', 'No hook available')}")
                            st.write(f"**Inspired by:** {rec.get('inspired_by', 'Unknown')}")
                            st.write(f"**Performance:** {rec.get('performance_score', 'N/A')}")
                            st.write(f"**Why this angle:** {rec.get('why_this_angle', 'N/A')}")
                            st.write("**Script Outline:**")
                            outline = rec.get("outline", [])
                            for step in outline:
                                st.write(f"- {step}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the backend server. Please ensure the FastAPI server is running on port 8000.")
            except requests.exceptions.JSONDecodeError:
                st.error("Failed to receive valid response from server. Please check the API key and ensure the backend is running.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
