from unittest.mock import AsyncMock, patch

import httpx
import pytest
from httpx import AsyncClient
from tenacity import Future, RetryError

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
async def test_cycle_update_plane_error_returns_400(
    client: AsyncClient, plane_client_mock: AsyncMock
) -> None:
    request = httpx.Request(
        "PATCH", "https://api.plane.so/api/v1/workspaces/x/projects/p/cycles/c/"
    )
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
    assert (
        client._workspace_path("projects/pid/cycles/")
        == "/workspaces/workspace-slug/projects/pid/cycles/"
    )


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


@pytest.mark.asyncio
async def test_append_description_when_get_cycle_404() -> None:
    client = PlaneClient(
        base_url="https://api.plane.so/api/v1",
        api_token="plane_api_test",
        workspace_slug="workspace-slug",
        project_id="project-id",
    )
    request = httpx.Request(
        "GET",
        "https://api.plane.so/api/v1/workspaces/workspace-slug/projects/project-id/cycles/c1/",
    )
    response = httpx.Response(404, request=request)
    http_err = httpx.HTTPStatusError("not found", request=request, response=response)
    attempt = Future(attempt_number=3)
    attempt.set_exception(http_err)

    with patch.object(
        client,
        "get_cycle",
        new=AsyncMock(side_effect=RetryError(attempt)),
    ):
        with patch.object(client, "_request", new=AsyncMock(return_value={"id": "c1"})) as mocked:
            result = await client.append_cycle_description(
                cycle_id="c1",
                summary_text="standup line",
            )

    assert result.description == "standup line"
    assert mocked.await_args.kwargs["json"]["description"] == "standup line"
    await client.aclose()


@pytest.mark.asyncio
async def test_create_work_item_valid(client: AsyncClient) -> None:
    payload = {
        "name": "Transfer funds",
        "description_html": "<p>As a user...</p>",
        "project_id": "proj-1",
    }
    response = await client.post("/api/plane/work-item", headers=AUTH, json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] == "wi-123"


@pytest.mark.asyncio
async def test_create_work_item_missing_name(client: AsyncClient) -> None:
    payload = {"description_html": "<p>As a user...</p>"}
    response = await client.post("/api/plane/work-item", headers=AUTH, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_work_item_plane_error_returns_400(
    client: AsyncClient, plane_client_mock: AsyncMock
) -> None:
    request = httpx.Request(
        "POST",
        "https://api.plane.so/api/v1/workspaces/x/projects/p/work-items/",
    )
    response = httpx.Response(status_code=500, request=request)
    plane_client_mock.create_work_item.side_effect = httpx.HTTPStatusError(
        "Plane failed",
        request=request,
        response=response,
    )
    payload = {"name": "Story", "description_html": "<p>body</p>"}
    result = await client.post("/api/plane/work-item", headers=AUTH, json=payload)
    assert result.status_code == 400
    assert result.json()["success"] is False


@pytest.mark.asyncio
async def test_create_work_item_calls_plane() -> None:
    client = PlaneClient(
        base_url="https://api.plane.so/api/v1",
        api_token="plane_api_test",
        workspace_slug="workspace-slug",
        project_id="default-project",
    )
    with patch.object(
        client,
        "_request",
        new=AsyncMock(
            return_value={
                "id": "wi-1",
                "name": "Login story",
                "description_html": "<p>criteria</p>",
            },
        ),
    ) as mocked:
        result = await client.create_work_item(
            name="Login story",
            description_html="<p>criteria</p>",
            project_id="custom-project",
        )

    assert result.id == "wi-1"
    assert result.name == "Login story"
    mocked.assert_awaited_once_with(
        "POST",
        "projects/custom-project/work-items/",
        json={"name": "Login story", "description_html": "<p>criteria</p>"},
    )
    await client.aclose()
