from enum import Enum
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class ENVIRONMENT(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"

class Settings(BaseSettings):
  ENVIRONMENT: ENVIRONMENT        # a custom Enum ("development" or "production")
  DATABASE_URL: str             # a string that contains the database URL
  JWT_SECRET: str               # a string that contains the JWT secret   
  CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
  CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
  
  class Config:
    env_file = ".env"
    
settings = Settings()
