from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.agent", "../.env.agent"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    SUPABASE_URL: AnyHttpUrl
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_DATABASE_URL: str = ""

    PLANE_API_BASE_URL: AnyHttpUrl = "https://api.plane.so/api/v1"
    PLANE_API_TOKEN: str
    PLANE_WORKSPACE_SLUG: str
    PLANE_PROJECT_ID: str

    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-3.1-pro"
    GEMINI_MAX_OUTPUT_TOKENS: int = Field(default=512, ge=64, le=4096)

    STANDUP_CRON: str = "45 8 * * 1-5"
    STANDUP_TIMEZONE: str = "Asia/Colombo"
    AGENT_N8N_WEBHOOK_SECRET: str

    GITHUB_TOKEN: str
    GITHUB_REPO: str

    CORS_ALLOW_ORIGINS: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
