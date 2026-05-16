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
    get_github_client,
    get_memory_store,
    get_participant_store,
    get_plane_client,
)
from app.core.config import get_settings
from app.model.blocker import Blocker, BlockerSource, BlockerStatus
from app.model.memory import CompactedSprintMemory, MemoryCompactResponse
from app.model.participant import Participant, ParticipantRole
from app.model.plane import CycleUpdateResult, PlaneMember
from app.model.standup import CommitFile, CommitStats, GitCommit

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


def _participant(
    plane_user_id: str,
    display_name: str,
    email: str,
    github_login: str,
    role: ParticipantRole = ParticipantRole.DEVELOPER,
) -> Participant:
    return Participant(
        plane_user_id=plane_user_id,
        display_name=display_name,
        email=email,
        github_login=github_login,
        role=role,
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
    participants = {
        "usr_alice_biometrics": _participant(
            "usr_alice_biometrics",
            "Alice",
            "alice@example.com",
            "alice",
        ),
        "usr_bob_payment": _participant(
            "usr_bob_payment",
            "Bob",
            "bob@example.com",
            "bob",
        ),
        "usr_carol_dashboard": _participant(
            "usr_carol_dashboard",
            "Carol",
            "carol@example.com",
            "carol",
        ),
    }

    async def _get_by_plane_user_id(user_id: str) -> Participant | None:
        return participants.get(user_id)

    store.get_by_plane_user_id.side_effect = _get_by_plane_user_id
    return store


@pytest.fixture
def blocker_store_mock() -> AsyncMock:
    store = AsyncMock()
    default = _default_blocker()
    store.report.return_value = default
    store.update.return_value = default
    store.resolve.return_value = default
    async def _list_active(
        sprint_id: str | None = None,
        participant_id: str | None = None,
    ) -> list[Blocker]:
        if participant_id == "usr_bob_payment":
            return [
                Blocker(
                    key="bob-ci-flakiness",
                    participant_id="usr_bob_payment",
                    sprint_id=sprint_id,
                    description="CI test flakiness on payment endpoints impacting deployment",
                    status=BlockerStatus.ACTIVE,
                    source=BlockerSource.STANDUP,
                )
            ]
        return []

    store.list_active.side_effect = _list_active
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
    store.latest_summary.return_value = "Previous summary"

    async def _upsert_context(payload):  # noqa: ANN001
        return payload

    store.upsert_context.side_effect = _upsert_context
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
    client.list_project_members.return_value = [
        PlaneMember(id="usr_alice_biometrics", display_name="Alice", email="alice@example.com"),
        PlaneMember(id="usr_bob_payment", display_name="Bob", email="bob@example.com"),
        PlaneMember(id="usr_carol_dashboard", display_name="Carol", email="carol@example.com"),
    ]
    client.aclose.return_value = None
    return client


@pytest.fixture
def github_client_mock() -> AsyncMock:
    client = AsyncMock()

    async def _commits_since(github_login: str | None, email: str | None, since):  # noqa: ANN001
        if github_login == "alice":
            return [
                GitCommit(
                    sha="commit1",
                    message="feat(biometrics): add FaceID enrollment flow",
                    url="github.com/repo/financeflow/commits/1",
                    date="2026-05-16T00:00:00Z",
                    author_name="Alice",
                    author_email=email,
                    stats=CommitStats(total=10, additions=8, deletions=2),
                    files=[
                        CommitFile(
                            filename="app/biometrics.py",
                            status="modified",
                            additions=8,
                            deletions=2,
                            changes=10,
                            patch="@@ -1 +1 @@\n-old\n+new",
                        )
                    ],
                ),
                GitCommit(
                    sha="commit2",
                    message="fix(biometrics): handle cancelled auth",
                    url="github.com/repo/financeflow/commits/2",
                    date="2026-05-16T01:00:00Z",
                    author_name="Alice",
                    author_email=email,
                    stats=CommitStats(total=6, additions=5, deletions=1),
                    files=[
                        CommitFile(
                            filename="app/auth.py",
                            status="modified",
                            additions=5,
                            deletions=1,
                            changes=6,
                            patch="@@ -2 +2 @@\n-old\n+new",
                        )
                    ],
                ),
            ]
        if github_login == "bob":
            return [
                GitCommit(
                    sha="commit3",
                    message="fix(payment-timeout): add circuit breaker",
                    url="github.com/repo/financeflow/commits/3",
                    date="2026-05-16T02:00:00Z",
                    author_name="Bob",
                    author_email=email,
                    stats=CommitStats(total=12, additions=9, deletions=3),
                    files=[
                        CommitFile(
                            filename="app/payments.py",
                            status="modified",
                            additions=9,
                            deletions=3,
                            changes=12,
                            patch="@@ -3 +3 @@\n-old\n+new",
                        )
                    ],
                ),
                GitCommit(
                    sha="commit4",
                    message="fix(payment-timeout): flaky test WIP",
                    url="github.com/repo/financeflow/commits/4",
                    date="2026-05-16T03:00:00Z",
                    author_name="Bob",
                    author_email=email,
                    stats=CommitStats(total=7, additions=6, deletions=1),
                    files=[
                        CommitFile(
                            filename="tests/test_payments.py",
                            status="modified",
                            additions=6,
                            deletions=1,
                            changes=7,
                            patch="@@ -4 +4 @@\n-old\n+new",
                        )
                    ],
                ),
            ]
        if github_login == "carol":
            return [
                GitCommit(
                    sha="commit5",
                    message="feat(dashboard): transaction list component",
                    url="github.com/repo/financeflow/commits/5",
                    date="2026-05-16T04:00:00Z",
                    author_name="Carol",
                    author_email=email,
                    stats=CommitStats(total=5, additions=5, deletions=0),
                    files=[
                        CommitFile(
                            filename="app/dashboard.py",
                            status="added",
                            additions=5,
                            deletions=0,
                            changes=5,
                            patch="@@ -0,0 +1,5 @@\n+line1\n+line2",
                        )
                    ],
                ),
            ]
        return []

    async def _latest_commit(github_login: str | None, email: str | None):  # noqa: ANN001
        if github_login:
            return GitCommit(
                sha=f"{github_login}-latest",
                message=f"chore: latest for {github_login}",
                url=f"github.com/repo/financeflow/commits/{github_login}-latest",
                date="2026-05-14T00:00:00Z",
                author_name=github_login.title(),
                author_email=email,
                stats=CommitStats(total=2, additions=2, deletions=0),
                files=[
                    CommitFile(
                        filename="README.md",
                        status="modified",
                        additions=2,
                        deletions=0,
                        changes=2,
                        patch="@@ -1 +1,2 @@\n old\n+new",
                    )
                ],
            )
        return None

    client.commits_since.side_effect = _commits_since
    client.latest_commit.side_effect = _latest_commit
    return client


@pytest.fixture
async def client(
    test_env: None,
    participant_store_mock: AsyncMock,
    blocker_store_mock: AsyncMock,
    memory_store_mock: AsyncMock,
    gemini_client_mock: AsyncMock,
    plane_client_mock: AsyncMock,
    github_client_mock: AsyncMock,
) -> AsyncGenerator[AsyncClient]:
    from app.main import create_app

    app = create_app()
    app.state.supabase = MagicMock()
    app.dependency_overrides[get_participant_store] = lambda: participant_store_mock
    app.dependency_overrides[get_blocker_store] = lambda: blocker_store_mock
    app.dependency_overrides[get_memory_store] = lambda: memory_store_mock
    app.dependency_overrides[get_gemini_client] = lambda: gemini_client_mock
    app.dependency_overrides[get_plane_client] = lambda: plane_client_mock
    app.dependency_overrides[get_github_client] = lambda: github_client_mock
    app.dependency_overrides[deps.get_supabase] = lambda: MagicMock()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client

    app.dependency_overrides.clear()
