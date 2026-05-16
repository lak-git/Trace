from supabase import AsyncClient

from app.model.participant import Participant, ParticipantUpsert


class ParticipantStore:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def upsert(self, payload: ParticipantUpsert) -> Participant:
        res = await self._client.table("participants").upsert(
            payload.model_dump(mode="json"),
            on_conflict="plane_user_id",
        ).execute()
        row = res.data[0] if isinstance(res.data, list) else res.data
        return Participant.model_validate(row)

    async def list_active(self) -> list[Participant]:
        res = await self._client.table("participants").select("*").eq("active", True).execute()
        return [Participant.model_validate(row) for row in (res.data or [])]

    async def get_by_plane_user_id(self, plane_user_id: str) -> Participant | None:
        res = await self._client.table("participants").select("*").eq(
            "plane_user_id",
            plane_user_id,
        ).limit(1).execute()
        if not res.data:
            return None
        return Participant.model_validate(res.data[0])
