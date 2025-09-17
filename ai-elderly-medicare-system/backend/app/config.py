"""
Configuration settings for AI Elderly Medicare System
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    APP_NAME: str = "AI Elderly Medicare System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./elderly_medicare.db"
    DATABASE_ECHO: bool = False
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # AI/ML settings
    OPENAI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    ML_MODEL_PATH: str = "./ml_models"
    
    # Healthcare API settings
    FHIR_SERVER_URL: str = ""
    MEDICARE_API_KEY: str = ""
    
    # Email settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".jpg", ".jpeg", ".png", ".docx"]
    
    # Redis settings (for caching)
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_EXPIRE_SECONDS: int = 3600
    
    # Monitoring settings
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Database configuration
DATABASE_CONFIG = {
    "url": settings.DATABASE_URL,
    "echo": settings.DATABASE_ECHO,
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

# AI Model configurations
AI_MODELS = {
    "health_risk_assessment": {
        "model_name": "health_risk_classifier",
        "version": "1.0",
        "threshold": 0.7
    },
    "medication_interaction": {
        "model_name": "drug_interaction_detector",
        "version": "1.0",
        "threshold": 0.8
    },
    "symptom_analysis": {
        "model_name": "symptom_analyzer",
        "version": "1.0",
        "threshold": 0.6
    }
}

# Healthcare data validation rules
VALIDATION_RULES = {
    "age_range": {"min": 65, "max": 120},
    "blood_pressure": {
        "systolic": {"min": 70, "max": 250},
        "diastolic": {"min": 40, "max": 150}
    },
    "heart_rate": {"min": 40, "max": 200},
    "temperature": {"min": 95.0, "max": 110.0},
    "blood_sugar": {"min": 50, "max": 600}
}