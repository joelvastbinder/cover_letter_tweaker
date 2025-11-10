import os
from dotenv import load_dotenv


class Config:
    load_dotenv()
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
    MAX_TEXT_LENGTH = 50000
    GEMINI_MODEL = "gemini-2.5-flash"

