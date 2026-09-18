import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the backend directory, regardless of where the process is started from
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_FILE, override=True)

class Settings:
    PROJECT_NAME: str = "AI Admission Counselling Agent"
    VERSION: str = "1.0.0"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "false").lower() in ("1", "true", "yes")
    MONGODB_URL: str = os.getenv("MONGODB_URL", "")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "admission_counselling")

settings = Settings()
