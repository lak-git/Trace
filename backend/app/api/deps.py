from typing import Annotated

from fastapi import Depends
from supabase import AsyncClient

from app.core.config import Settings, get_settings
from app.database import get_supabase
from app.service.blocker_store import BlockerStore
from app.service.gemini_client import GeminiClient
from app.service.github_client import GitHubClient
from app.service.memory_store import MemoryStore
from app.service.participant_store import ParticipantStore
from app.service.plane_client import PlaneClient

SettingsDep = Annotated[Settings, Depends(get_settings)]
SupabaseDep = Annotated[AsyncClient, Depends(get_supabase)]


def get_participant_store(client: SupabaseDep) -> ParticipantStore:
    return ParticipantStore(client)


def get_blocker_store(client: SupabaseDep) -> BlockerStore:
    return BlockerStore(client)


def get_memory_store(client: SupabaseDep) -> MemoryStore:
    return MemoryStore(client)


def get_plane_client(settings: SettingsDep) -> PlaneClient:
    return PlaneClient(
        base_url=str(settings.PLANE_API_BASE_URL),
        api_token=settings.PLANE_API_TOKEN,
        workspace_slug=settings.PLANE_WORKSPACE_SLUG,
        project_id=settings.PLANE_PROJECT_ID,
    )


def get_github_client(settings: SettingsDep) -> GitHubClient:
    return GitHubClient(
        token=settings.GITHUB_TOKEN,
        repo=settings.GITHUB_REPO,
    )


def get_gemini_client(settings: SettingsDep) -> GeminiClient:
    return GeminiClient(
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL,
        max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
    )
