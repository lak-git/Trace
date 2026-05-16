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
