# core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    OPENDOTA_API_KEY: str = os.getenv("OPENDOTA_API_KEY")
    STRATZ_API_KEY: str = os.getenv("STRATZ_API_KEY")
    HOST_ID: int = int(os.getenv("HOST_ID", "0"))
    DATABASE_URL: str = os.getenv("DATABASE_URL")

settings = Settings()
