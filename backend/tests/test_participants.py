from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.model.participant import Participant, ParticipantRole, ParticipantUpsert
from app.service.participant_store import ParticipantStore
from tests.conftest import AUTH


def _participant(plane_user_id: str, name: str, role: ParticipantRole) -> Participant:
    return Participant(
        plane_user_id=plane_user_id,
        display_name=name,
        role=role,
        email=f"{name.lower().replace(' ', '.')}@example.com",
        github_login=name.lower().replace(" ", ""),
        active=True,
    )


@pytest.mark.asyncio
async def test_upsert_valid_developer(
    client: AsyncClient, participant_store_mock: AsyncMock
) -> None:
    expected = _participant("usr_dev", "Dev User", ParticipantRole.DEVELOPER)
    participant_store_mock.upsert.return_value = expected
    payload = {
        "plane_user_id": "usr_dev",
        "display_name": "Dev User",
        "email": "dev@example.com",
        "github_login": "devuser",
        "role": "developer",
    }
    response = await client.post("/api/participants", headers=AUTH, json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["plane_user_id"] == payload["plane_user_id"]
    assert body["data"]["display_name"] == payload["display_name"]
    assert body["data"]["role"] == payload["role"]


@pytest.mark.asyncio
async def test_upsert_valid_ba(client: AsyncClient) -> None:
    payload = {"plane_user_id": "usr_ba", "display_name": "BA User", "role": "ba"}
    response = await client.post("/api/participants", headers=AUTH, json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_upsert_valid_qa(client: AsyncClient) -> None:
    payload = {"plane_user_id": "usr_qa", "display_name": "QA User", "role": "qa"}
    response = await client.post("/api/participants", headers=AUTH, json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_upsert_missing_plane_user_id(client: AsyncClient) -> None:
    payload = {"display_name": "No ID", "role": "developer"}
    response = await client.post("/api/participants", headers=AUTH, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_upsert_missing_display_name(client: AsyncClient) -> None:
    payload = {"plane_user_id": "usr_missing_name", "role": "developer"}
    response = await client.post("/api/participants", headers=AUTH, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_upsert_invalid_role(client: AsyncClient) -> None:
    payload = {"plane_user_id": "usr_pm", "display_name": "PM User", "role": "pm"}
    response = await client.post("/api/participants", headers=AUTH, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_upsert_store_raises_propagates_400(
    client: AsyncClient,
    participant_store_mock: AsyncMock,
) -> None:
    participant_store_mock.upsert.side_effect = RuntimeError("upsert failed")
    payload = {
        "plane_user_id": "usr_fail",
        "display_name": "Fail User",
        "role": "developer",
    }
    response = await client.post("/api/participants", headers=AUTH, json=payload)
    assert response.status_code == 400
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_list_returns_empty_list(
    client: AsyncClient, participant_store_mock: AsyncMock
) -> None:
    participant_store_mock.list_active.return_value = []
    response = await client.get("/api/participants", headers=AUTH)
    assert response.status_code == 200
    assert response.json() == {"success": True, "data": []}


@pytest.mark.asyncio
async def test_list_returns_participants(
    client: AsyncClient, participant_store_mock: AsyncMock
) -> None:
    participant_store_mock.list_active.return_value = [
        _participant("usr_1", "Alice", ParticipantRole.DEVELOPER),
        _participant("usr_2", "Bob", ParticipantRole.BA),
    ]
    response = await client.get("/api/participants", headers=AUTH)
    body = response.json()
    assert response.status_code == 200
    assert len(body["data"]) == 2


@pytest.mark.asyncio
async def test_store_upsert_calls_supabase() -> None:
    execute = AsyncMock(
        return_value=SimpleNamespace(
            data=[
                {
                    "plane_user_id": "usr_1",
                    "display_name": "Alice",
                    "role": "developer",
                    "active": True,
                }
            ]
        )
    )
    table = MagicStoreChain(execute=execute)
    client = SimpleNamespace(table=MagicMock(return_value=table))
    store = ParticipantStore(client)  # type: ignore[arg-type]

    payload = ParticipantUpsert(
        plane_user_id="usr_1", display_name="Alice", role=ParticipantRole.DEVELOPER
    )
    await store.upsert(payload)

    client.table.assert_called_once_with("participants")
    table.upsert.assert_called_once()
    assert table.upsert.call_args.kwargs["on_conflict"] == "plane_user_id"
    execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_store_list_active_filters_by_active_true() -> None:
    execute = AsyncMock(return_value=SimpleNamespace(data=[]))
    table = MagicStoreChain(execute=execute)
    client = SimpleNamespace(table=MagicMock(return_value=table))
    store = ParticipantStore(client)  # type: ignore[arg-type]

    await store.list_active()

    table.eq.assert_called_once_with("active", True)
    execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_store_get_by_plane_user_id_returns_none_when_empty() -> None:
    execute = AsyncMock(return_value=SimpleNamespace(data=[]))
    table = MagicStoreChain(execute=execute)
    client = SimpleNamespace(table=MagicMock(return_value=table))
    store = ParticipantStore(client)  # type: ignore[arg-type]

    result = await store.get_by_plane_user_id("usr_none")
    assert result is None


@pytest.mark.asyncio
async def test_store_get_by_plane_user_id_returns_participant_when_found() -> None:
    execute = AsyncMock(
        return_value=SimpleNamespace(
            data=[
                {
                    "plane_user_id": "usr_found",
                    "display_name": "Found User",
                    "role": "developer",
                    "active": True,
                }
            ]
        )
    )
    table = MagicStoreChain(execute=execute)
    client = SimpleNamespace(table=MagicMock(return_value=table))
    store = ParticipantStore(client)  # type: ignore[arg-type]

    result = await store.get_by_plane_user_id("usr_found")
    assert isinstance(result, Participant)
    assert result.plane_user_id == "usr_found"


class MagicStoreChain:
    def __init__(self, execute: AsyncMock) -> None:
        self.upsert = MagicMock(return_value=self)
        self.select = MagicMock(return_value=self)
        self.eq = MagicMock(return_value=self)
        self.limit = MagicMock(return_value=self)
        self.execute = execute
