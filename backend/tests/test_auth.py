import pytest
from httpx import AsyncClient

from tests.conftest import BAD_AUTH

PROTECTED_ROUTES: list[tuple[str, str, dict[str, object] | None]] = [
    ("GET", "/api/context/prefetch?cycle_id=x", None),
    ("GET", "/api/participants", None),
    (
        "POST",
        "/api/participants",
        {
            "plane_user_id": "usr_test",
            "display_name": "User Test",
            "role": "developer",
        },
    ),
    (
        "POST",
        "/api/blocker/report",
        {
            "participant_id": "usr_test",
            "description": "Blocked by CI",
            "source": "standup",
        },
    ),
    ("GET", "/api/blockers/active", None),
    (
        "POST",
        "/api/memory/compact",
        {
            "sprint_id": "sprint-7",
            "transcript": "Did work today.",
        },
    ),
    (
        "POST",
        "/api/memory/upsert",
        {
            "participant_id": "usr_test",
            "sprint_id": "sprint-7",
            "standup_date": "2026-05-16",
            "summary": "Summary",
            "importance": 2,
        },
    ),
    ("GET", "/api/memory/sprint-7", None),
    (
        "POST",
        "/api/plane/cycle-update",
        {
            "cycle_id": "sprint-7",
            "summary_text": "Standup summary",
        },
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("method,path,body", PROTECTED_ROUTES)
async def test_missing_secret_header_returns_422(
    client: AsyncClient,
    method: str,
    path: str,
    body: dict[str, object] | None,
) -> None:
    response = await client.request(method=method, url=path, json=body)
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize("method,path,body", PROTECTED_ROUTES)
async def test_wrong_secret_returns_401(
    client: AsyncClient,
    method: str,
    path: str,
    body: dict[str, object] | None,
) -> None:
    response = await client.request(method=method, url=path, headers=BAD_AUTH, json=body)
    assert response.status_code == 401
