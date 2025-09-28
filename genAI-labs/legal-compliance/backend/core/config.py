"""
Configuration management for Legal Compliance AI Platform
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Legal Compliance AI Platform"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://legal_user:legal_password@localhost:5432/legal_compliance"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    CACHE_TTL: int = 3600  # 1 hour
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # LLM API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # Legal Knowledge Base
    LEGAL_KNOWLEDGE_BASE_URL: str = "https://api.legal-knowledge-base.com"
    LEGAL_KNOWLEDGE_BASE_KEY: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = True
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "docx", "txt", "md"]
    
    # Legal Context
    DEFAULT_JURISDICTION: str = "US"
    SUPPORTED_JURISDICTIONS: List[str] = [
        "US", "UK", "EU", "DE", "FR", "IT", "ES", "CA", "AU"
    ]
    
    # LLM Configuration
    DEFAULT_LLM_MODELS: List[str] = [
        "gpt-4-turbo-preview",
        "claude-3-5-sonnet-20241022",
        "gemini-pro"
    ]
    
    # Response Configuration
    MAX_RESPONSE_TOKENS: int = 4000
    RESPONSE_TEMPERATURE: float = 0.1  # Low temperature for legal accuracy
    RESPONSE_TOP_P: float = 0.9
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("SUPPORTED_JURISDICTIONS", pre=True)
    def assemble_jurisdictions(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("DEFAULT_LLM_MODELS", pre=True)
    def assemble_models(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("ALLOWED_FILE_TYPES", pre=True)
    def assemble_file_types(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings"""
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    CACHE_TTL: int = 300  # 5 minutes for faster development


class ProductionSettings(Settings):
    """Production environment settings"""
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CACHE_TTL: int = 3600  # 1 hour
    PROMETHEUS_ENABLED: bool = True


class TestingSettings(Settings):
    """Testing environment settings"""
    ENVIRONMENT: str = "testing"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DATABASE_URL: str = "postgresql://legal_user:legal_password@localhost:5432/legal_compliance_test"
    CACHE_TTL: int = 60  # 1 minute for testing


def get_environment_settings() -> Settings:
    """Get environment-specific settings"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()
