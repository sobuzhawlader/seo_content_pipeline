import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
UNSPLASH_CLIENT_ID = os.getenv("UNSPLASH_CLIENT_ID", "")
WP_URL = os.getenv("WP_URL", "")
WP_USERNAME = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")
CUSTOM_WEBHOOK_URL = os.getenv("CUSTOM_WEBHOOK_URL", "")
CUSTOM_WEBHOOK_SECRET = os.getenv("CUSTOM_WEBHOOK_SECRET", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///seo_pipeline.db")
