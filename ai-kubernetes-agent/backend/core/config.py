from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    kubeconfig_path: str = str(Path.home() / ".kube" / "config")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()