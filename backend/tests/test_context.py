import pytest
from httpx import AsyncClient

from tests.conftest import AUTH


@pytest.mark.asyncio
async def test_prefetch_requires_cycle_id(client: AsyncClient) -> None:
    response = await client.get("/api/context/prefetch", headers=AUTH)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_prefetch_returns_three_participants(client: AsyncClient) -> None:
    response = await client.get("/api/context/prefetch?cycle_id=sprint-7", headers=AUTH)
    data = response.json()["data"]
    assert response.status_code == 200
    assert len(data) == 3


@pytest.mark.asyncio
async def test_prefetch_first_participant_shape(client: AsyncClient) -> None:
    response = await client.get("/api/context/prefetch?cycle_id=sprint-7", headers=AUTH)
    alice = response.json()["data"][0]
    assert alice["sprint_id"] == "sprint-7"
    assert alice["participant_id"] == "usr_alice_biometrics"
    assert len(alice["commits"]) == 2
    assert len(alice["blockers"]) == 0
    assert alice["last_summary"] is not None


@pytest.mark.asyncio
async def test_prefetch_bob_has_one_active_blocker(client: AsyncClient) -> None:
    response = await client.get("/api/context/prefetch?cycle_id=sprint-7", headers=AUTH)
    bob = response.json()["data"][1]
    assert len(bob["blockers"]) == 1
    assert bob["blockers"][0]["status"] == "active"
    assert bob["blockers"][0]["key"] == "bob-ci-flakiness"


@pytest.mark.asyncio
async def test_prefetch_carol_has_one_commit(client: AsyncClient) -> None:
    response = await client.get("/api/context/prefetch?cycle_id=sprint-7", headers=AUTH)
    carol = response.json()["data"][2]
    assert len(carol["commits"]) == 1


@pytest.mark.asyncio
async def test_prefetch_project_id_optional(client: AsyncClient) -> None:
    response = await client.get(
        "/api/context/prefetch?cycle_id=sprint-7&project_id=demo",
        headers=AUTH,
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 3


@pytest.mark.asyncio
async def test_prefetch_envelope(client: AsyncClient) -> None:
    response = await client.get("/api/context/prefetch?cycle_id=sprint-7", headers=AUTH)
    payload = response.json()
    assert payload["success"] is True
    assert isinstance(payload["data"], list)


@pytest.mark.asyncio
async def test_prefetch_idempotent(client: AsyncClient) -> None:
    first = await client.get("/api/context/prefetch?cycle_id=sprint-7", headers=AUTH)
    second = await client.get("/api/context/prefetch?cycle_id=sprint-7", headers=AUTH)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()


@pytest.mark.asyncio
async def test_prefetch_does_not_persist_raw_commits(client: AsyncClient, memory_store_mock) -> None:
    await client.get("/api/context/prefetch?cycle_id=sprint-7", headers=AUTH)
    memory_store_mock.upsert_context.assert_not_called()


@pytest.mark.asyncio
async def test_compact_commits_returns_summaries(client: AsyncClient) -> None:
    prefetch = await client.get("/api/context/prefetch?cycle_id=sprint-7", headers=AUTH)
    alice = prefetch.json()["data"][0]
    compiled = await client.post(
        "/api/context/commits/compact",
        headers=AUTH,
        json={
            "sprint_id": alice["sprint_id"],
            "participant_id": alice["participant_id"],
            "display_name": "Alice",
            "commits": [
                {
                    "sha": commit["sha"],
                    "message": commit["message"],
                    "url": commit["url"],
                    "date": commit["date"],
                }
                for commit in alice["commits"]
            ],
            "has_recent_commits": True,
        },
    )
    assert compiled.status_code == 200
    payload = compiled.json()["data"]
    assert len(payload["commits"]) == 2
    assert all(commit["summary"] for commit in payload["commits"])
    assert payload["activity_summary"]


@pytest.mark.asyncio
async def test_store_context_requires_compacted_summaries(client: AsyncClient) -> None:
    response = await client.post(
        "/api/context/store",
        headers=AUTH,
        json={
            "sprint_id": "sprint-7",
            "participant_id": "usr_alice_biometrics",
            "commits": [
                {
                    "sha": "commit1",
                    "message": "feat: biometrics",
                    "url": "https://example/commit1",
                    "date": "2026-05-16T08:00:00+00:00",
                }
            ],
            "blockers": [],
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_store_context_persists_compacted_commits(
    client: AsyncClient,
    memory_store_mock,
) -> None:
    response = await client.post(
        "/api/context/store",
        headers=AUTH,
        json={
            "sprint_id": "sprint-7",
            "participant_id": "usr_alice_biometrics",
            "commits": [
                {
                    "sha": "commit1",
                    "message": "feat: biometrics",
                    "url": "https://example/commit1",
                    "date": "2026-05-16T08:00:00+00:00",
                    "summary": "Implemented FaceID flow scaffolding.",
                }
            ],
            "blockers": [],
            "last_summary": "Previous summary",
        },
    )
    assert response.status_code == 200
    memory_store_mock.upsert_context.assert_called_once()
