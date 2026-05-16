import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.deps import get_participant_store
from app.core.auth import verify_webhook_secret
from app.model.participant import ParticipantUpsert
from app.service.participant_store import ParticipantStore

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/participants",
    tags=["participants"],
    dependencies=[Depends(verify_webhook_secret)],
)

ParticipantStoreDep = Annotated[ParticipantStore, Depends(get_participant_store)]


@router.post("", response_model=None)
async def upsert_participant(
    payload: ParticipantUpsert,
    store: ParticipantStoreDep,
) -> dict[str, object] | JSONResponse:
    try:
        participant = await store.upsert(payload)
        return {"success": True, "data": participant.model_dump(mode="json")}
    except Exception as exc:
        logger.exception("Failed to upsert participant")
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)


@router.get("", response_model=None)
async def list_participants(store: ParticipantStoreDep) -> dict[str, object] | JSONResponse:
    try:
        participants = await store.list_active()
        return {"success": True, "data": [item.model_dump(mode="json") for item in participants]}
    except Exception as exc:
        logger.exception("Failed to list participants")
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)
