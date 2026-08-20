from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="OMNIMIND_", extra="ignore")

    data_dir: Path = BASE_DIR / "data"
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'omnimind.db'}"
    cors_origins: list[str] = ["http://localhost:8080", "http://localhost:3000"]

    jira_base_url: Optional[str] = None
    jira_email: Optional[str] = None
    jira_api_token: Optional[str] = None
    jira_project_key: Optional[str] = None

    github_token: Optional[str] = None
    github_repo: Optional[str] = None

    slack_webhook_url: Optional[str] = None


settings = Settings()

for _sub in ("uploads", "audio", "exports"):
    (settings.data_dir / _sub).mkdir(parents=True, exist_ok=True)
