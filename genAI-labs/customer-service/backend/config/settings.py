"""
Application settings and configuration
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "GenAI Customer Service"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    
    # AWS Configuration
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    
    # AWS Services
    BEDROCK_MODEL_ID: str = Field(
        default="anthropic.claude-3-5-sonnet-20241022-v2:0",
        env="BEDROCK_MODEL_ID"
    )
    BEDROCK_REGION: str = Field(default="us-east-1", env="BEDROCK_REGION")
    
    # Database
    MONGODB_URL: str = Field(..., env="MONGODB_URL")
    MONGODB_DATABASE: str = Field(default="customer_service", env="MONGODB_DATABASE")
    
    # Redis Cache
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # DynamoDB
    DYNAMODB_TABLE_PREFIX: str = Field(default="genai-cs", env="DYNAMODB_TABLE_PREFIX")
    
    # S3
    S3_BUCKET: str = Field(..., env="S3_BUCKET")
    S3_REGION: str = Field(default="us-east-1", env="S3_REGION")
    
    # OpenSearch
    OPENSEARCH_ENDPOINT: str = Field(..., env="OPENSEARCH_ENDPOINT")
    OPENSEARCH_INDEX: str = Field(default="knowledge-base", env="OPENSEARCH_INDEX")
    
    # AI Configuration
    MAX_TOKENS: int = Field(default=2000, env="MAX_TOKENS")
    TEMPERATURE: float = Field(default=0.7, env="TEMPERATURE")
    CONFIDENCE_THRESHOLD: float = Field(default=0.8, env="CONFIDENCE_THRESHOLD")
    ESCALATION_THRESHOLD: float = Field(default=0.6, env="ESCALATION_THRESHOLD")
    
    # Voice AI
    TRANSCRIBE_LANGUAGE: str = Field(default="en-US", env="TRANSCRIBE_LANGUAGE")
    POLLY_VOICE_ID: str = Field(default="Joanna", env="POLLY_VOICE_ID")
    POLLY_ENGINE: str = Field(default="neural", env="POLLY_ENGINE")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
