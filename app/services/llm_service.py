import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from app.config import settings


def get_llm(model_name: Optional[str] = None, temperature: Optional[float] = None) -> BaseChatModel:
    """
    Instantiate and return the configured OpenAI Chat model.
    Throws a descriptive error if OPENAI_API_KEY is not set.
    """
    api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not configured. Please set OPENAI_API_KEY in your environment or .env file."
        )

    return ChatOpenAI(
        api_key=api_key,
        model=model_name or settings.openai_model_name,
        temperature=temperature if temperature is not None else settings.openai_temperature,
    )

