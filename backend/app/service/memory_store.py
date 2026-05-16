from datetime import date

from supabase import AsyncClient

from app.model.memory import AgentMemory, CompactedSprintMemory, MemoryUpsert, SprintMemoryFact
from app.model.standup import StandupContext
from app.service.blocker_store import BlockerStore
from app.service.participant_store import ParticipantStore


class MemoryStore:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def upsert_memory(self, payload: MemoryUpsert) -> AgentMemory:
        res = await self._client.table("agent_memory").upsert(
            payload.model_dump(mode="json"),
            on_conflict="participant_id,sprint_id,standup_date",
        ).execute()
        row = res.data[0] if isinstance(res.data, list) else res.data
        return AgentMemory.model_validate(row)

    async def list_memory(self, sprint_id: str, include_stale: bool = False) -> list[AgentMemory]:
        query = self._client.table("agent_memory").select("*").eq("sprint_id", sprint_id)
        if not include_stale:
            query = query.eq("stale", False)
        res = await query.order("created_at", desc=True).execute()
        return [AgentMemory.model_validate(row) for row in (res.data or [])]

    async def latest_summary(self, participant_id: str, sprint_id: str) -> str | None:
        res = await self._client.table("agent_memory").select("*").eq(
            "participant_id",
            participant_id,
        ).eq("sprint_id", sprint_id).eq("stale", False).order(
            "standup_date",
            desc=True,
        ).limit(1).execute()
        if not res.data:
            return None
        return AgentMemory.model_validate(res.data[0]).summary

    async def upsert_context(self, payload: StandupContext) -> StandupContext:
        row = payload.model_dump(mode="json", exclude_none=True)
        res = await self._client.table("standup_context").upsert(
            row,
            on_conflict="sprint_id,participant_id",
        ).execute()
        saved = res.data[0] if isinstance(res.data, list) else res.data
        return StandupContext.model_validate(saved)

    async def list_sprint_facts(self, sprint_id: str) -> list[SprintMemoryFact]:
        res = await self._client.table("sprint_memory").select("*").eq(
            "sprint_id",
            sprint_id,
        ).order("created_at", desc=False).execute()
        return [SprintMemoryFact.model_validate(row) for row in (res.data or [])]

    async def sprint_blob(self, sprint_id: str) -> CompactedSprintMemory:
        participants = await ParticipantStore(self._client).list_active()
        memory = await self.list_memory(sprint_id=sprint_id)
        blockers = await BlockerStore(self._client).list_active(sprint_id=sprint_id)
        facts = await self.list_sprint_facts(sprint_id=sprint_id)
        return CompactedSprintMemory(
            sprint_id=sprint_id,
            participants=participants,
            memory=memory,
            blockers=blockers,
            sprint_facts=facts,
        )

    async def mark_old_memory_stale(
        self,
        participant_id: str,
        sprint_id: str,
        before_date: date,
    ) -> None:
        await self._client.table("agent_memory").update({"stale": True}).eq(
            "participant_id",
            participant_id,
        ).eq("sprint_id", sprint_id).lt("standup_date", before_date.isoformat()).execute()
