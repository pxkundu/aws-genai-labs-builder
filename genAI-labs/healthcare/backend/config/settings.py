"""
Healthcare ChatGPT Clone - Configuration Settings
This module handles all application configuration and environment variables.
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Configuration
    APP_NAME: str = "Healthcare ChatGPT Clone"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="dev", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_PREFIX: str = "/api/v1"
    
    # Security Configuration
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ALLOWED_ORIGINS: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    
    # Database Configuration
    DB_HOST: str = Field(default="localhost", env="DB_HOST")
    DB_PORT: int = Field(default=5432, env="DB_PORT")
    DB_NAME: str = Field(default="healthcare_chat", env="DB_NAME")
    DB_USER: str = Field(default="postgres", env="DB_USER")
    DB_PASSWORD: str = Field(default="postgres", env="DB_PASSWORD")
    DB_SSL_MODE: str = Field(default="prefer", env="DB_SSL_MODE")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # AWS Configuration
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    
    # S3 Configuration
    S3_BUCKET: str = Field(default="healthcare-knowledge-base", env="S3_BUCKET")
    S3_PREFIX: str = Field(default="", env="S3_PREFIX")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    OPENAI_MAX_TOKENS: int = Field(default=2000, env="OPENAI_MAX_TOKENS")
    OPENAI_TEMPERATURE: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # AWS Bedrock Configuration
    BEDROCK_REGION: str = Field(default="us-east-1", env="BEDROCK_REGION")
    BEDROCK_MODEL_ID: str = Field(default="anthropic.claude-3-sonnet-20240229-v1:0", env="BEDROCK_MODEL_ID")
    
    # Healthcare-specific Configuration
    HEALTHCARE_MODE: bool = Field(default=True, env="HEALTHCARE_MODE")
    HIPAA_COMPLIANCE: bool = Field(default=True, env="HIPAA_COMPLIANCE")
    DATA_RETENTION_DAYS: int = Field(default=90, env="DATA_RETENTION_DAYS")
    
    # Chat Configuration
    MAX_CHAT_HISTORY: int = Field(default=50, env="MAX_CHAT_HISTORY")
    CHAT_TIMEOUT: int = Field(default=30, env="CHAT_TIMEOUT")
    ENABLE_CHAT_ANALYTICS: bool = Field(default=True, env="ENABLE_CHAT_ANALYTICS")
    
    # Knowledge Base Configuration
    KNOWLEDGE_BASE_UPDATE_INTERVAL: int = Field(default=3600, env="KNOWLEDGE_BASE_UPDATE_INTERVAL")  # 1 hour
    MAX_KNOWLEDGE_RESULTS: int = Field(default=10, env="MAX_KNOWLEDGE_RESULTS")
    
    # Monitoring Configuration
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        allowed_envs = ["dev", "staging", "prod"]
        if v not in allowed_envs:
            raise ValueError(f"Environment must be one of: {allowed_envs}")
        return v
    
    @property
    def database_url(self) -> str:
        """Get the complete database URL."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "prod"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "dev"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
