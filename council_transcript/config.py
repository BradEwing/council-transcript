"""Configuration management for the transcript pipeline."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Paths
    temp_dir: Path = Field(default=Path("./tmp"), alias="SMF_TEMP_DIR")
    transcripts_dir: Path = Field(default=Path("./transcripts"), alias="SMF_TRANSCRIPTS_DIR")
    reports_dir: Path = Field(default=Path("./reports"), alias="SMF_REPORTS_DIR")
    logs_dir: Path = Field(default=Path("./logs"), alias="SMF_LOGS_DIR")

    # Logging
    log_level: str = Field(default="INFO", alias="SMF_LOG_LEVEL")

    # Whisper model size (tiny, base, small, medium, large)
    whisper_model_size: str = Field(default="base", alias="SMF_WHISPER_MODEL_SIZE")

    class Config:
        env_file = ".env"
        case_sensitive = False
        populate_by_name = True

    def __init__(self, **data):
        super().__init__(**data)
        # Create required directories
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (cached after first call)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
