"""Configuration management for the Munger RAG Agent."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Keys
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    google_api_key: Optional[str] = Field(None, description="Google API key")
    huggingface_api_token: Optional[str] = Field(None, description="HuggingFace API token")
    pinecone_api_key: Optional[str] = Field(None, description="Pinecone API key")
    
    # Application Settings
    debug: bool = Field(False, description="Debug mode")
    log_level: str = Field("INFO", description="Logging level")
    development_mode: str = Field("local", description="Development mode")
    
    # URLs
    frontend_url: str = Field("http://localhost:3000", description="Frontend URL")
    backend_url: str = Field("http://localhost:8000", description="Backend URL")
    
    # Database
    database_url: str = Field("sqlite:///./munger_agent.db", description="Database URL")
    
    # Model Settings
    default_model: str = Field("gpt-4", description="Default AI model")
    embedding_model: str = Field("text-embedding-3-small", description="Embedding model")
    max_tokens: int = Field(4000, description="Maximum tokens per request")
    temperature: float = Field(0.7, description="Model temperature")
    
    # File Storage
    upload_dir: str = Field("./data/uploads", description="Upload directory")
    cache_dir: str = Field("./data/cache", description="Cache directory")


# Global settings instance
settings = Settings()
