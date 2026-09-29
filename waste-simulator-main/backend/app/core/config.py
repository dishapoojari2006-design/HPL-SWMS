import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

env_paths = [
    Path(__file__).resolve().parent.parent.parent / ".env",
    Path(__file__).resolve().parent.parent.parent.parent / ".env",
    Path.cwd() / ".env"
]
for p in env_paths:
    if p.exists():
        load_dotenv(dotenv_path=p, override=True)

class Settings:
    PROJECT_NAME: str = "Smart Waste Management Simulator (SWMS)"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/swms_db")
    if not DATABASE_URL.startswith("postgresql+") and DATABASE_URL.startswith("postgresql:"):
        DATABASE_URL = DATABASE_URL.replace("postgresql:", "postgresql+psycopg:", 1)
        
    JWT_SECRET: str = os.getenv("JWT_SECRET", "swms-super-secret-jwt-key-2026-production-grade")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "120"))
    
    CORS_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]
    
    DEFAULT_GROWTH_RATE: float = 2.0
    DEFAULT_PER_CAPITA_KG: float = 0.50
    DEFAULT_PER_HH_KG: float = 2.27

settings = Settings()
