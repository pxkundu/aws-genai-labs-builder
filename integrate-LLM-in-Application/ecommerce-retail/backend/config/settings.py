"""
Application Settings and Configuration
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "E-Commerce AI Platform"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    API_VERSION: str = "v1"
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"],
        env="ALLOWED_HOSTS"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/ecommerce",
        env="DATABASE_URL"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    REDIS_CACHE_TTL: int = Field(default=3600, env="REDIS_CACHE_TTL")  # 1 hour
    
    # LLM Configuration - OpenAI
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    OPENAI_MAX_TOKENS: int = Field(default=2000, env="OPENAI_MAX_TOKENS")
    OPENAI_TEMPERATURE: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # LLM Configuration - AWS Bedrock
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_ACCESS_KEY_ID: str = Field(default="", env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
    BEDROCK_MODEL_ID: str = Field(
        default="anthropic.claude-3-sonnet-20240229-v1:0",
        env="BEDROCK_MODEL_ID"
    )
    BEDROCK_REGION: str = Field(default="us-east-1", env="BEDROCK_REGION")
    
    # LLM Settings
    LLM_PROVIDER: str = Field(default="openai", env="LLM_PROVIDER")  # openai or bedrock
    LLM_CACHE_ENABLED: bool = Field(default=True, env="LLM_CACHE_ENABLED")
    LLM_MAX_RETRIES: int = Field(default=3, env="LLM_MAX_RETRIES")
    LLM_TIMEOUT: int = Field(default=30, env="LLM_TIMEOUT")
    
    # Vector Database (for RAG)
    VECTOR_DB_URL: str = Field(default="", env="VECTOR_DB_URL")
    VECTOR_DB_API_KEY: str = Field(default="", env="VECTOR_DB_API_KEY")
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        env="EMBEDDING_MODEL"
    )
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="json",
        env="LOG_FORMAT"
    )  # json or text
    
    # S3 Configuration (for product assets)
    AWS_S3_BUCKET: str = Field(default="", env="AWS_S3_BUCKET")
    AWS_S3_REGION: str = Field(default="us-east-1", env="AWS_S3_REGION")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


_settings: Settings = None


def get_settings() -> Settings:
    """Get application settings (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

