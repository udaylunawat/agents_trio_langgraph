"""
Shared utilities for the multi-agent AI system
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

def create_llm(llm_provider, model_name, api_key):
    """Create LLM instance based on provider"""
    if llm_provider == "OpenRouter":
        import httpx
        return ChatOpenAI(
            temperature=0.1,
            model=model_name,
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key="dummy_key",  # Required but will be overridden by headers
            default_headers={"Authorization": f"Bearer {api_key}"},
            http_client=httpx.Client(
                headers={"Authorization": f"Bearer {api_key}"}
            )
        )
    else:  # OpenAI
        return ChatOpenAI(
            temperature=0.1,
            model=model_name,
            openai_api_key=api_key
        )


def create_llm_youtube(llm_provider, model_name, api_key):
    """Create LLM instance for YouTube agent (different temperature)"""
    if llm_provider == "OpenRouter":
        import httpx
        return ChatOpenAI(
            temperature=0.7,
            model=model_name,
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key="dummy_key",  # Required but will be overridden by headers
            default_headers={"Authorization": f"Bearer {api_key}"},
            http_client=httpx.Client(
                headers={"Authorization": f"Bearer {api_key}"}
            )
        )
    else:  # OpenAI
        return ChatOpenAI(
            temperature=0.7,
            model=model_name,
            openai_api_key=api_key
        )


def get_health_implication(aqi):
    """Get health implication for AQI value"""
    if aqi <= 50:
        return "Air quality is good. No health impacts expected."
    elif aqi <= 100:
        return "Air quality is moderate. Some people may experience mild health effects."
    elif aqi <= 150:
        return "Air quality is unhealthy for sensitive groups. Children, elderly, and those with respiratory conditions should limit outdoor activities."
    else:
        return "Air quality is unhealthy. Everyone should avoid prolonged outdoor activities."
