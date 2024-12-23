from functools import lru_cache
from pydantic_settings import BaseSettings
import os
from typing import Final,Dict

class Setting(BaseSettings):
    RECIPE_DB_API_KEY: Final[str]
    PINECONE_API_KEY: Final[str]
    PINECONE_HOST_URL: Final[str]
    OPENAI_API_KEY: Final[str]
    
    #추가설정
    RABBITMQ_HOST : Final[str]
    RABBITMQ_QUEUE : str = "recommendation.queue"
    RABBITMQ_RESPONSE_QUEUE : str = "response.queue"
    RABBITMQ_EXCHANGE: str = "recommendation.exchange"
    RABBITMQ_ROUTING_KEY: str = "recommendation.zipbob"
    RABBITMQ_DLX: str = "dlx.rc.exchange"
    RABBITMQ_QUEUE_ARGUMENTS : Dict[str,any] = {
    'x-message-ttl': 60000,  # 60초
    'x-dead-letter-exchange': 'dlx.rc.exchange',
    'x-dead-letter-routing-key': 'dlq.rc.zipbob',
    'x-queue-type': 'classic'
    }
    MODEL_NAME: str = "intfloat/multilingual-e5-large-instruct"
    VECTOR_DB_NAME : str = "recipes"
    VECTOR_DIMENSION: int = 1024
    DEFAULT_TOP_K: int = 500
    LOG_LEVEL: str = "INFO"


    class Config:
        env_file = os.getenv("ENV_FILE", ".env")
        frozen = True  # 불변 객체로 만들기

@lru_cache()
def get_settings() -> Setting:
    return Setting()

setting = get_settings()