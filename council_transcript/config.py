"""Configuration management for the transcript pipeline."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Paths
    temp_dir: Path = Path("./tmp")
    transcripts_dir: Path = Path("./transcripts")
    logs_dir: Path = Path("./logs")

    # Logging
    log_level: str = "INFO"

    # Whisper model size (tiny, base, small, medium, large)
    whisper_model_size: str = "base"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **data):
        super().__init__(**data)
        # Create required directories
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (cached after first call)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
