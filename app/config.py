from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

CODE_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_DIR = CODE_DIR.parent
ENV_PATH = CODE_DIR / ".env"
load_dotenv(ENV_PATH)


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from code/.env and environment variables."""

    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    tavily_api_key: str | None = os.getenv("TAVILY_API_KEY")
    langsmith_tracing: bool = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    langsmith_project: str = os.getenv("LANGSMITH_PROJECT", "lca-lc-foundations")
    sqlite_path: Path = Path(
        os.getenv("APP_SQLITE_PATH", str(CODE_DIR / "data" / "app.db"))
    )
    model_name: str = os.getenv("APP_MODEL", "gpt-5-nano")
    mcp_timezone: str = os.getenv("MCP_TIMEZONE", "America/New_York")


settings = Settings()


def ensure_data_directory() -> Path:
    settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return settings.sqlite_path
