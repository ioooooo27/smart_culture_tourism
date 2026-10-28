from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    MYSQL_HOST:str=os.getenv("MYSQL_HOST")
    MYSQL_PORT:int=int(os.getenv("MYSQL_PORT"))
    MYSQL_USER:str=os.getenv("MYSQL_USER")
    MYSQL_PASSWORD:str=os.getenv("MYSQL_PASSWORD")
    MYSQL_DB:str=os.getenv("MYSQL_DB")

    REDIS_HOST:str=os.getenv("REDIS_HOST")
    REDIS_PORT:int=int(os.getenv("REDIS_PORT"))

    LLM_API_KEY:str=os.getenv("LLM_API_KEY")
    LLM_BASE_URL:str=os.getenv("LLM_BASE_URL")

settings=Settings()
