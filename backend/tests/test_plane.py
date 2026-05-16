from unittest.mock import AsyncMock, patch

import httpx
import pytest
from httpx import AsyncClient

from app.model.plane import PlaneCycle
from app.service.plane_client import PlaneClient
from tests.conftest import AUTH


@pytest.mark.asyncio
async def test_cycle_update_valid(client: AsyncClient) -> None:
    payload = {"cycle_id": "sprint-7", "summary_text": "Daily standup summary"}
    response = await client.post("/api/plane/cycle-update", headers=AUTH, json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_cycle_update_missing_cycle_id(client: AsyncClient) -> None:
    payload = {"summary_text": "Daily standup summary"}
    response = await client.post("/api/plane/cycle-update", headers=AUTH, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_cycle_update_missing_summary_text(client: AsyncClient) -> None:
    payload = {"cycle_id": "sprint-7"}
    response = await client.post("/api/plane/cycle-update", headers=AUTH, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_cycle_update_plane_error_returns_400(client: AsyncClient, plane_client_mock: AsyncMock) -> None:
    request = httpx.Request("PATCH", "https://api.plane.so/api/v1/workspaces/x/projects/p/cycles/c/")
    response = httpx.Response(status_code=500, request=request)
    plane_client_mock.append_cycle_description.side_effect = httpx.HTTPStatusError(
        "Plane failed",
        request=request,
        response=response,
    )
    payload = {"cycle_id": "sprint-7", "summary_text": "Daily standup summary"}
    result = await client.post("/api/plane/cycle-update", headers=AUTH, json=payload)
    assert result.status_code == 400
    assert result.json()["success"] is False


def test_workspace_path_construction() -> None:
    client = PlaneClient(
        base_url="https://api.plane.so/api/v1",
        api_token="plane_api_test",
        workspace_slug="workspace-slug",
        project_id="project-id",
    )
    assert client._workspace_path("projects/pid/cycles/") == "/workspaces/workspace-slug/projects/pid/cycles/"


@pytest.mark.asyncio
async def test_append_description_concatenates() -> None:
    client = PlaneClient(
        base_url="https://api.plane.so/api/v1",
        api_token="plane_api_test",
        workspace_slug="workspace-slug",
        project_id="project-id",
    )
    with patch.object(
        client,
        "_request",
        new=AsyncMock(side_effect=[{"id": "c1", "description": "existing"}, {"id": "c1"}]),
    ) as mocked:
        result = await client.append_cycle_description(
            cycle_id="c1",
            summary_text="new summary",
        )

    assert result.description == "existing\n\nnew summary"
    patch_call = mocked.await_args_list[1]
    assert patch_call.args[0] == "PATCH"
    assert patch_call.kwargs["json"]["description"] == "existing\n\nnew summary"
    await client.aclose()


@pytest.mark.asyncio
async def test_append_description_when_no_existing() -> None:
    client = PlaneClient(
        base_url="https://api.plane.so/api/v1",
        api_token="plane_api_test",
        workspace_slug="workspace-slug",
        project_id="project-id",
    )

    async def fake_get_cycle(cycle_id: str, project_id: str | None = None) -> PlaneCycle:
        return PlaneCycle(id=cycle_id, description=None)

    with patch.object(client, "get_cycle", new=AsyncMock(side_effect=fake_get_cycle)):
        with patch.object(client, "_request", new=AsyncMock(return_value={"id": "c1"})) as mocked:
            result = await client.append_cycle_description(
                cycle_id="c1",
                summary_text="only new text",
            )

    assert result.description == "only new text"
    assert mocked.await_args.kwargs["json"]["description"] == "only new text"
    await client.aclose()
