"""Configuration management for the transcript pipeline."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: str

    # LLM Configuration
    llm_model: str = "claude-opus-4-6"
    temperature: float = 0.7

    # Transcription Configuration
    enable_whisper_fallback: bool = False
    enable_claude_transcription: bool = True

    # Paths
    temp_dir: Path = Path("./tmp")
    transcripts_dir: Path = Path("./transcripts")
    logs_dir: Path = Path("./logs")

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **data):
        super().__init__(**data)
        # Create required directories
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()
