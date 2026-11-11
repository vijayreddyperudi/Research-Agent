import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model_name: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))

    max_research_rounds: int = int(os.getenv("MAX_RESEARCH_ROUNDS", "3"))
    min_useful_sources: int = int(os.getenv("MIN_USEFUL_SOURCES", "5"))

    internal_docs_path: str = os.getenv("INTERNAL_DOCS_PATH", "./data/internal_docs")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    streamlit_port: int = int(os.getenv("STREAMLIT_PORT", "8501"))


settings = Settings()

