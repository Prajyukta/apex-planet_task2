"""Typed application configuration loaded from environment variables."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


def get_settings() -> Settings:
    """Load required database settings without hard-coding credentials."""
    required = {
        "postgres_user": os.getenv("POSTGRES_USER", "analytics"),
        "postgres_password": os.getenv("POSTGRES_PASSWORD", "analytics_password"),
        "postgres_db": os.getenv("POSTGRES_DB", "ecommerce"),
    }
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    return Settings(**required, postgres_port=port)
