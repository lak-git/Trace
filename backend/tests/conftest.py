from collections.abc import AsyncGenerator
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api import deps
from app.api.deps import (
    get_blocker_store,
    get_gemini_client,
    get_memory_store,
    get_participant_store,
    get_plane_client,
)
from app.core.config import get_settings
from app.main import create_app
from app.model.blocker import Blocker, BlockerSource, BlockerStatus
from app.model.memory import CompactedSprintMemory, MemoryCompactResponse
from app.model.participant import Participant, ParticipantRole
from app.model.plane import CycleUpdateResult

TEST_SECRET = "test-secret"
AUTH = {"X-Agent-Secret": TEST_SECRET}
BAD_AUTH = {"X-Agent-Secret": "wrong"}


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_N8N_WEBHOOK_SECRET", TEST_SECRET)
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "dummy-service-role")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "dummy-anon")
    monkeypatch.setenv("SUPABASE_DATABASE_URL", "postgresql://demo")
    monkeypatch.setenv("PLANE_API_BASE_URL", "https://api.plane.so/api/v1")
    monkeypatch.setenv("PLANE_API_TOKEN", "plane_api_test")
    monkeypatch.setenv("PLANE_WORKSPACE_SLUG", "demo-workspace")
    monkeypatch.setenv("PLANE_PROJECT_ID", "demo-project")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-gemini")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.1-pro")
    monkeypatch.setenv("GITHUB_TOKEN", "dummy-gh")
    monkeypatch.setenv("GITHUB_REPO", "owner/repo")


def _default_participant() -> Participant:
    return Participant(
        plane_user_id="usr_default",
        display_name="Default User",
        email="default@example.com",
        github_login="default",
        role=ParticipantRole.DEVELOPER,
        active=True,
    )


def _default_blocker() -> Blocker:
    return Blocker(
        key="default-blocker",
        participant_id="usr_default",
        sprint_id="sprint-7",
        description="Default blocker",
        status=BlockerStatus.ACTIVE,
        source=BlockerSource.MANUAL,
        last_update="Default blocker",
    )


@pytest.fixture
def participant_store_mock() -> AsyncMock:
    store = AsyncMock()
    store.upsert.return_value = _default_participant()
    store.list_active.return_value = []
    store.get_by_plane_user_id.return_value = None
    return store


@pytest.fixture
def blocker_store_mock() -> AsyncMock:
    store = AsyncMock()
    default = _default_blocker()
    store.report.return_value = default
    store.update.return_value = default
    store.resolve.return_value = default
    store.list_active.return_value = []
    return store


@pytest.fixture
def memory_store_mock() -> AsyncMock:
    store = AsyncMock()
    blob = CompactedSprintMemory(
        sprint_id="sprint-7",
        participants=[],
        memory=[],
        blockers=[],
        sprint_facts=[],
    )
    store.upsert_memory.return_value = SimpleNamespace(
        model_dump=lambda mode="json": {
            "participant_id": "usr_default",
            "sprint_id": "sprint-7",
            "standup_date": date(2026, 5, 16).isoformat(),
            "summary": "Default memory",
            "importance": 1,
            "stale": False,
        }
    )
    store.sprint_blob.return_value = blob
    return store


@pytest.fixture
def gemini_client_mock() -> AsyncMock:
    client = AsyncMock()
    client.compact_standup_segment.return_value = MemoryCompactResponse(
        summary="Compacted standup summary",
        importance=2,
    )
    return client


@pytest.fixture
def plane_client_mock() -> AsyncMock:
    client = AsyncMock()
    client.append_cycle_description.return_value = CycleUpdateResult(
        cycle_id="sprint-7",
        description="Existing\n\nNew summary",
        raw={"ok": True},
    )
    client.aclose.return_value = None
    return client


@pytest.fixture
async def client(
    test_env: None,
    participant_store_mock: AsyncMock,
    blocker_store_mock: AsyncMock,
    memory_store_mock: AsyncMock,
    gemini_client_mock: AsyncMock,
    plane_client_mock: AsyncMock,
) -> AsyncGenerator[AsyncClient]:
    app = create_app()
    app.state.supabase = MagicMock()
    app.dependency_overrides[get_participant_store] = lambda: participant_store_mock
    app.dependency_overrides[get_blocker_store] = lambda: blocker_store_mock
    app.dependency_overrides[get_memory_store] = lambda: memory_store_mock
    app.dependency_overrides[get_gemini_client] = lambda: gemini_client_mock
    app.dependency_overrides[get_plane_client] = lambda: plane_client_mock
    app.dependency_overrides[deps.get_supabase] = lambda: MagicMock()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client

    app.dependency_overrides.clear()
