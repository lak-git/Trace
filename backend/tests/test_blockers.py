from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.model.blocker import BlockerReport, BlockerResolve, BlockerSource, BlockerStatus, BlockerUpdate
from app.service.blocker_store import BlockerStore, _make_blocker_key
from tests.conftest import AUTH


@pytest.mark.asyncio
async def test_report_valid_payload(client: AsyncClient) -> None:
    payload = {
        "participant_id": "usr_alice",
        "description": "CI keeps failing on payment tests",
        "source": "standup",
    }
    response = await client.post("/api/blocker/report", headers=AUTH, json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_report_missing_participant_id(client: AsyncClient) -> None:
    payload = {"description": "No participant", "source": "manual"}
    response = await client.post("/api/blocker/report", headers=AUTH, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_report_missing_description(client: AsyncClient) -> None:
    payload = {"participant_id": "usr_alice", "source": "manual"}
    response = await client.post("/api/blocker/report", headers=AUTH, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_report_invalid_source(client: AsyncClient) -> None:
    payload = {"participant_id": "usr_alice", "description": "Blocked", "source": "twitter"}
    response = await client.post("/api/blocker/report", headers=AUTH, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_report_store_error_returns_400(client: AsyncClient, blocker_store_mock: AsyncMock) -> None:
    blocker_store_mock.report.side_effect = RuntimeError("db failure")
    payload = {"participant_id": "usr_alice", "description": "Blocked", "source": "manual"}
    response = await client.post("/api/blocker/report", headers=AUTH, json=payload)
    assert response.status_code == 400
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_update_valid(client: AsyncClient) -> None:
    response = await client.post(
        "/api/blocker/some-key/update",
        headers=AUTH,
        json={"last_update": "Still blocked, awaiting review"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_empty_last_update(client: AsyncClient) -> None:
    response = await client.post(
        "/api/blocker/some-key/update",
        headers=AUTH,
        json={"last_update": ""},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_not_found(client: AsyncClient, blocker_store_mock: AsyncMock) -> None:
    blocker_store_mock.update.side_effect = KeyError("Blocker not found: some-key")
    response = await client.post(
        "/api/blocker/some-key/update",
        headers=AUTH,
        json={"last_update": "No record"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_store_error_returns_400(client: AsyncClient, blocker_store_mock: AsyncMock) -> None:
    blocker_store_mock.update.side_effect = RuntimeError("Unexpected")
    response = await client.post(
        "/api/blocker/some-key/update",
        headers=AUTH,
        json={"last_update": "Attempting update"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_resolve_valid_no_body(client: AsyncClient) -> None:
    response = await client.post("/api/blocker/some-key/resolve", headers=AUTH, json={})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_resolve_with_resolution_text(client: AsyncClient) -> None:
    response = await client.post(
        "/api/blocker/some-key/resolve",
        headers=AUTH,
        json={"resolution": "Fixed by pinning flaky dependency"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_resolve_not_found(client: AsyncClient, blocker_store_mock: AsyncMock) -> None:
    blocker_store_mock.resolve.side_effect = KeyError("Blocker not found: some-key")
    response = await client.post("/api/blocker/some-key/resolve", headers=AUTH, json={})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_active_no_filter(client: AsyncClient, blocker_store_mock: AsyncMock) -> None:
    blocker_store_mock.list_active.return_value = []
    response = await client.get("/api/blockers/active", headers=AUTH)
    assert response.status_code == 200
    assert response.json() == {"success": True, "data": []}


@pytest.mark.asyncio
async def test_list_active_filter_by_sprint_id(client: AsyncClient, blocker_store_mock: AsyncMock) -> None:
    response = await client.get("/api/blockers/active?sprint_id=sprint-7", headers=AUTH)
    assert response.status_code == 200
    blocker_store_mock.list_active.assert_awaited_once_with(
        sprint_id="sprint-7",
        participant_id=None,
    )


@pytest.mark.asyncio
async def test_list_active_filter_by_participant_id(client: AsyncClient, blocker_store_mock: AsyncMock) -> None:
    response = await client.get("/api/blockers/active?participant_id=usr_alice", headers=AUTH)
    assert response.status_code == 200
    blocker_store_mock.list_active.assert_awaited_once_with(
        sprint_id=None,
        participant_id="usr_alice",
    )


def test_key_uses_explicit_key_when_provided() -> None:
    report = BlockerReport(participant_id="usr", description="desc", key="My Blocker")
    assert _make_blocker_key(report) == "my-blocker"


def test_key_auto_generated_from_participant_and_description() -> None:
    report = BlockerReport(participant_id="usr_bob_payment", description="CI test flakiness")
    key = _make_blocker_key(report)
    assert key.startswith("usr-bob-payment-")
    assert "ci-test-flakiness" in key


def test_key_truncates_long_participant_id() -> None:
    participant_id = "participant_" + ("x" * 50)
    report = BlockerReport(participant_id=participant_id, description="Short desc")
    key = _make_blocker_key(report)
    prefix = key.split("-short-desc")[0]
    assert len(prefix) <= 24


def test_key_truncates_long_description() -> None:
    description = "Very long blocker description " + ("x" * 100)
    report = BlockerReport(participant_id="usr", description=description)
    key = _make_blocker_key(report)
    body = key.split("-", maxsplit=1)[1]
    assert len(body) <= 48


@pytest.mark.asyncio
async def test_report_sets_status_to_active() -> None:
    table = QueryChain(
        execute_result=SimpleNamespace(
            data=[
                {
                    "key": "custom-key",
                    "participant_id": "usr_alice",
                    "description": "Blocked",
                    "status": BlockerStatus.ACTIVE.value,
                    "source": BlockerSource.MANUAL.value,
                    "last_update": "Blocked",
                }
            ]
        )
    )
    client = MagicMock()
    client.table.return_value = table
    store = BlockerStore(client)  # type: ignore[arg-type]

    await store.report(BlockerReport(participant_id="usr_alice", description="Blocked"))

    row = table.upsert.call_args.args[0]
    assert row["status"] == "active"


@pytest.mark.asyncio
async def test_report_default_last_update_from_description() -> None:
    table = QueryChain(
        execute_result=SimpleNamespace(
            data=[
                {
                    "key": "custom-key",
                    "participant_id": "usr_alice",
                    "description": "Blocked due to flaky tests",
                    "status": BlockerStatus.ACTIVE.value,
                    "source": BlockerSource.MANUAL.value,
                    "last_update": "Blocked due to flaky tests",
                }
            ]
        )
    )
    client = MagicMock()
    client.table.return_value = table
    store = BlockerStore(client)  # type: ignore[arg-type]

    await store.report(
        BlockerReport(
            participant_id="usr_alice",
            description="Blocked due to flaky tests",
            last_update=None,
        )
    )

    row = table.upsert.call_args.args[0]
    assert row["last_update"] == "Blocked due to flaky tests"


class QueryChain:
    def __init__(self, execute_result: object) -> None:
        self.upsert = MagicMock(return_value=self)
        self.update = MagicMock(return_value=self)
        self.eq = MagicMock(return_value=self)
        self.order = MagicMock(return_value=self)
        self.execute = AsyncMock(return_value=execute_result)
