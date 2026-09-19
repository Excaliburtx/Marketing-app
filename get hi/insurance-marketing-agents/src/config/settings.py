"""Application settings loaded from environment variables."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    default_model: str = "gpt-4o"

    # Optional tools
    serper_api_key: str | None = None

    # Paths
    data_dir: Path = Path("./data")
    reports_dir: Path = Path("./reports")

    # Product lines this system supports
    product_lines: list[str] = ["pre-need", "at-need", "annuities"]


settings = Settings()
