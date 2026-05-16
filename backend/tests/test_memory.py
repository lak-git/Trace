from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.model.memory import MemoryCompactResponse
from app.service.gemini_client import GeminiClient
from tests.conftest import AUTH


@pytest.mark.asyncio
async def test_compact_valid_transcript(client: AsyncClient) -> None:
    payload = {"sprint_id": "sprint-7", "transcript": "Yesterday finished API wiring."}
    response = await client.post("/api/memory/compact", headers=AUTH, json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "summary" in body["data"]
    assert "importance" in body["data"]


@pytest.mark.asyncio
async def test_compact_empty_transcript(client: AsyncClient) -> None:
    payload = {"sprint_id": "sprint-7", "transcript": ""}
    response = await client.post("/api/memory/compact", headers=AUTH, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_compact_gemini_error_returns_400(client: AsyncClient, gemini_client_mock: AsyncMock) -> None:
    gemini_client_mock.compact_standup_segment.side_effect = RuntimeError("gemini failed")
    payload = {"sprint_id": "sprint-7", "transcript": "Anything"}
    response = await client.post("/api/memory/compact", headers=AUTH, json=payload)
    assert response.status_code == 400
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_upsert_valid_payload(client: AsyncClient) -> None:
    payload = {
        "participant_id": "usr_alice",
        "sprint_id": "sprint-7",
        "standup_date": "2026-05-16",
        "summary": "Finished auth endpoint tests.",
        "importance": 2,
    }
    response = await client.post("/api/memory/upsert", headers=AUTH, json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_upsert_importance_below_range(client: AsyncClient) -> None:
    payload = {
        "participant_id": "usr_alice",
        "sprint_id": "sprint-7",
        "standup_date": "2026-05-16",
        "summary": "text",
        "importance": 0,
    }
    response = await client.post("/api/memory/upsert", headers=AUTH, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_upsert_importance_above_range(client: AsyncClient) -> None:
    payload = {
        "participant_id": "usr_alice",
        "sprint_id": "sprint-7",
        "standup_date": "2026-05-16",
        "summary": "text",
        "importance": 4,
    }
    response = await client.post("/api/memory/upsert", headers=AUTH, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_upsert_missing_standup_date(client: AsyncClient) -> None:
    payload = {
        "participant_id": "usr_alice",
        "sprint_id": "sprint-7",
        "summary": "text",
        "importance": 2,
    }
    response = await client.post("/api/memory/upsert", headers=AUTH, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_upsert_store_error_returns_400(client: AsyncClient, memory_store_mock: AsyncMock) -> None:
    memory_store_mock.upsert_memory.side_effect = RuntimeError("store fail")
    payload = {
        "participant_id": "usr_alice",
        "sprint_id": "sprint-7",
        "standup_date": "2026-05-16",
        "summary": "text",
        "importance": 2,
    }
    response = await client.post("/api/memory/upsert", headers=AUTH, json=payload)
    assert response.status_code == 400
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_get_blob_returns_compacted_memory(client: AsyncClient, memory_store_mock: AsyncMock) -> None:
    response = await client.get("/api/memory/sprint-7", headers=AUTH)
    assert response.status_code == 200
    payload = response.json()["data"]
    for key in ("sprint_id", "participants", "memory", "blockers", "sprint_facts"):
        assert key in payload
    memory_store_mock.sprint_blob.assert_awaited_once_with("sprint-7")


@pytest.mark.asyncio
async def test_get_blob_store_error_returns_400(client: AsyncClient, memory_store_mock: AsyncMock) -> None:
    memory_store_mock.sprint_blob.side_effect = RuntimeError("blob failure")
    response = await client.get("/api/memory/sprint-7", headers=AUTH)
    assert response.status_code == 400
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_compact_parses_valid_json_response() -> None:
    gemini = GeminiClient(api_key="k", model="m", max_output_tokens=256)
    gemini._client = MagicMock()
    gemini._client.aio = MagicMock()
    gemini._client.aio.models = MagicMock()
    gemini._client.aio.models.generate_content = AsyncMock(
        return_value=SimpleNamespace(text='{"summary":"done","importance":2}')
    )

    result = await gemini.compact_standup_segment("Transcript")

    assert isinstance(result, MemoryCompactResponse)
    assert result.summary == "done"
    assert result.importance == 2


@pytest.mark.asyncio
async def test_compact_falls_back_on_non_json() -> None:
    gemini = GeminiClient(api_key="k", model="m", max_output_tokens=256)
    gemini._client = MagicMock()
    gemini._client.aio = MagicMock()
    gemini._client.aio.models = MagicMock()
    gemini._client.aio.models.generate_content = AsyncMock(
        return_value=SimpleNamespace(text="plain text response")
    )

    result = await gemini.compact_standup_segment("Transcript")

    assert result.summary == "plain text response"
    assert result.importance == 1
