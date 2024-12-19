from functools import lru_cache
from pydantic_settings import BaseSettings
import os
from typing import Final

class Setting(BaseSettings):
    RECIPE_DB_API_KEY: Final[str]
    PINECONE_API_KEY: Final[str]
    PINECONE_HOST_URL: Final[str]
    OPENAI_API_KEY: Final[str]
    
    class Config:
        env_file = os.getenv("ENV_FILE", ".env")
        frozen = True  # 불변 객체로 만들기

@lru_cache()
def get_settings() -> Setting:
    return Setting()

setting = get_settings()