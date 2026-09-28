import os
from dotenv import load_dotenv

load_dotenv()

def get_config_val(key: str, default: str = "") -> str:
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default

GEMINI_API_KEY = get_config_val("GEMINI_API_KEY", "")
SERPER_API_KEY = get_config_val("SERPER_API_KEY", "")
UNSPLASH_CLIENT_ID = get_config_val("UNSPLASH_CLIENT_ID", "")
WP_URL = get_config_val("WP_URL", "")
WP_USERNAME = get_config_val("WP_USERNAME", "")
WP_APP_PASSWORD = get_config_val("WP_APP_PASSWORD", "")
CUSTOM_WEBHOOK_URL = get_config_val("CUSTOM_WEBHOOK_URL", "")
CUSTOM_WEBHOOK_SECRET = get_config_val("CUSTOM_WEBHOOK_SECRET", "")
DATABASE_URL = get_config_val("DATABASE_URL", "sqlite:///seo_pipeline.db")

def get_genai_client(api_key: str = None):
    from google import genai
    key = api_key or get_config_val("GEMINI_API_KEY", "")
    if key:
        return genai.Client(api_key=key)
    try:
        return genai.Client()
    except Exception as e:
        raise ValueError(
            "Gemini API key is required. Please set GEMINI_API_KEY in environment or Streamlit Secrets."
        ) from e
