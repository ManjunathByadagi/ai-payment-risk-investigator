import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Payment Risk Investigator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./risk_investigator.db")
    CORS_ORIGINS: List[str] = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")]
    
    LLM_AVAILABLE: bool = os.getenv("LLM_AVAILABLE", "false").lower() in ("true", "1", "yes")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    LOW_RISK_THRESHOLD: float = float(os.getenv("LOW_RISK_THRESHOLD", 0.30))
    HIGH_RISK_THRESHOLD: float = float(os.getenv("HIGH_RISK_THRESHOLD", 0.70))
    FALSE_POSITIVE_COST: float = float(os.getenv("FALSE_POSITIVE_COST", 50.0))

settings = Settings()
