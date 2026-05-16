import asyncio
import logging
import time
from email.utils import parsedate_to_datetime
from typing import Any

import httpx
from tenacity import RetryError, retry, stop_after_attempt, wait_exponential

from app.model.plane import CycleUpdateResult, PlaneCycle, PlaneMember, WorkItemCreateResult

logger = logging.getLogger(__name__)


class PlaneClient:
    def __init__(
        self,
        base_url: str,
        api_token: str,
        workspace_slug: str,
        project_id: str,
    ) -> None:
        self._workspace_slug = workspace_slug
        self._project_id = project_id
        self._last_request_at = 0.0
        self._lock = asyncio.Lock()
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={
                "X-API-Key": api_token,
                "Content-Type": "application/json",
            },
            timeout=20,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _throttle(self) -> None:
        async with self._lock:
            loop = asyncio.get_running_loop()
            now = loop.time()
            elapsed = now - self._last_request_at
            if elapsed < 1:
                await asyncio.sleep(1 - elapsed)
            self._last_request_at = loop.time()

    async def _respect_rate_limit(self, response: httpx.Response) -> None:
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        if remaining != "0" or not reset:
            return
        try:
            reset_at = parsedate_to_datetime(reset).timestamp()
        except (TypeError, ValueError):
            try:
                reset_at = float(reset)
            except ValueError:
                return
        sleep_for = max(0.0, reset_at - time.time())
        if sleep_for:
            await asyncio.sleep(min(sleep_for, 60))

    def _workspace_path(self, suffix: str) -> str:
        clean = suffix.lstrip("/")
        return f"/workspaces/{self._workspace_slug}/{clean}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _request(
        self,
        method: str,
        suffix: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        await self._throttle()
        try:
            response = await self._client.request(
                method,
                self._workspace_path(suffix),
                params=params,
                json=json,
            )
            await self._respect_rate_limit(response)
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.exception("Plane returned an error for %s %s", method, suffix)
            raise
        except httpx.RequestError:
            logger.exception("Plane request failed for %s %s", method, suffix)
            raise
        return response.json()

    async def get_cycle(self, cycle_id: str, project_id: str | None = None) -> PlaneCycle:
        pid = project_id or self._project_id
        payload = await self._request("GET", f"projects/{pid}/cycles/{cycle_id}/")
        return PlaneCycle.model_validate(payload)

    async def list_project_members(self, project_id: str | None = None) -> list[PlaneMember]:
        pid = project_id or self._project_id
        payload = await self._request("GET", f"projects/{pid}/project-members/")
        items = payload.get("results", payload if isinstance(payload, list) else [])
        members: list[PlaneMember] = []
        for item in items:
            member = item.get("member") or item.get("user") or item
            member_id = str(member.get("id") or item.get("member_id") or item.get("id"))
            members.append(
                PlaneMember(
                    id=member_id,
                    display_name=member.get("display_name")
                    or member.get("first_name")
                    or member.get("email"),
                    email=member.get("email"),
                ),
            )
        return members

    async def _fetch_cycle_description_or_empty(
        self,
        cycle_id: str,
        project_id: str,
    ) -> str:
        try:
            cycle = await self.get_cycle(cycle_id=cycle_id, project_id=project_id)
            return cycle.description or ""
        except RetryError as retry_err:
            last = retry_err.last_attempt
            exc = last.exception() if hasattr(last, "exception") else last
            if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 404:
                logger.warning(
                    "Plane GET cycle %s returned 404; appending summary without prior text",
                    cycle_id,
                )
                return ""
            raise

    async def append_cycle_description(
        self,
        cycle_id: str,
        summary_text: str,
        project_id: str | None = None,
    ) -> CycleUpdateResult:
        pid = project_id or self._project_id
        current = await self._fetch_cycle_description_or_empty(cycle_id, pid)
        description = f"{current.rstrip()}\n\n{summary_text.strip()}".strip()
        payload = await self._request(
            "PATCH",
            f"projects/{pid}/cycles/{cycle_id}/",
            json={"description": description},
        )
        return CycleUpdateResult(cycle_id=cycle_id, description=description, raw=payload)

    async def create_work_item(
        self,
        name: str,
        description_html: str,
        project_id: str | None = None,
    ) -> WorkItemCreateResult:
        pid = project_id or self._project_id
        payload = await self._request(
            "POST",
            f"projects/{pid}/work-items/",
            json={"name": name, "description_html": description_html},
        )
        return WorkItemCreateResult(
            id=str(payload.get("id", "")),
            name=payload.get("name"),
            description_html=payload.get("description_html"),
            raw=payload,
        )
