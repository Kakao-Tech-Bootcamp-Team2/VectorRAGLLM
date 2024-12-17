from pydantic_settings import BaseSettings
import os

class Setting(BaseSettings) : 
    RECIPE_DB_API_KEY : str
    PINECONE_API_KEY : str
    PINECONE_HOST_URL : str
    OPENAI_API_KEY : str
    class Config :
        env_file = os.getenv("ENV_FILE",".env")

setting = Setting()