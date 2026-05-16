from datetime import UTC, datetime

from slugify import slugify
from supabase import AsyncClient

from app.model.blocker import Blocker, BlockerReport, BlockerResolve, BlockerStatus, BlockerUpdate


def _make_blocker_key(report: BlockerReport) -> str:
    if report.key:
        return slugify(report.key)
    prefix = slugify(report.participant_id)[:24]
    body = slugify(report.description)[:48]
    return f"{prefix}-{body}".strip("-")


class BlockerStore:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def report(self, payload: BlockerReport) -> Blocker:
        row = payload.model_dump(mode="json")
        row["key"] = _make_blocker_key(payload)
        row["status"] = BlockerStatus.ACTIVE.value
        if not row.get("last_update"):
            row["last_update"] = payload.description

        res = await self._client.table("blockers").upsert(
            row,
            on_conflict="key",
        ).execute()
        saved = res.data[0] if isinstance(res.data, list) else res.data
        return Blocker.model_validate(saved)

    async def update(self, key: str, payload: BlockerUpdate) -> Blocker:
        update = payload.model_dump(mode="json", exclude_none=True)
        res = await self._client.table("blockers").update(update).eq("key", key).execute()
        if not res.data:
            raise KeyError(f"Blocker not found: {key}")
        return Blocker.model_validate(res.data[0])

    async def resolve(self, key: str, payload: BlockerResolve) -> Blocker:
        update = {
            "status": BlockerStatus.RESOLVED.value,
            "resolved_at": datetime.now(UTC).isoformat(),
        }
        if payload.resolution:
            update["last_update"] = payload.resolution
        if payload.github_url:
            update["github_url"] = payload.github_url

        res = await self._client.table("blockers").update(update).eq("key", key).execute()
        if not res.data:
            raise KeyError(f"Blocker not found: {key}")
        return Blocker.model_validate(res.data[0])

    async def list_active(
        self,
        sprint_id: str | None = None,
        participant_id: str | None = None,
    ) -> list[Blocker]:
        query = self._client.table("blockers").select("*").eq("status", BlockerStatus.ACTIVE.value)
        if sprint_id:
            query = query.eq("sprint_id", sprint_id)
        if participant_id:
            query = query.eq("participant_id", participant_id)
        res = await query.order("updated_at", desc=True).execute()
        return [Blocker.model_validate(row) for row in (res.data or [])]
