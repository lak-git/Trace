import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.deps import get_gemini_client, get_memory_store
from app.core.auth import verify_webhook_secret
from app.model.memory import MemoryCompactRequest, MemoryUpsert
from app.service.gemini_client import GeminiClient
from app.service.memory_store import MemoryStore

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/memory",
    tags=["memory"],
    dependencies=[Depends(verify_webhook_secret)],
)

MemoryStoreDep = Annotated[MemoryStore, Depends(get_memory_store)]
GeminiClientDep = Annotated[GeminiClient, Depends(get_gemini_client)]


@router.post("/compact", response_model=None)
async def compact_memory(
    payload: MemoryCompactRequest,
    gemini: GeminiClientDep,
) -> dict[str, object] | JSONResponse:
    try:
        summary = await gemini.compact_standup_segment(payload.transcript)
        return {"success": True, "data": summary.model_dump(mode="json")}
    except Exception as exc:
        logger.exception("Failed to compact memory")
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)


@router.post("/upsert", response_model=None)
async def upsert_memory(
    payload: MemoryUpsert,
    store: MemoryStoreDep,
) -> dict[str, object] | JSONResponse:
    try:
        memory = await store.upsert_memory(payload)
        return {"success": True, "data": memory.model_dump(mode="json")}
    except Exception as exc:
        logger.exception("Failed to upsert memory")
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)


@router.get("/{sprint_id}", response_model=None)
async def get_memory_blob(
    sprint_id: str,
    store: MemoryStoreDep,
) -> dict[str, object] | JSONResponse:
    try:
        blob = await store.sprint_blob(sprint_id)
        return {"success": True, "data": blob.model_dump(mode="json")}
    except Exception as exc:
        logger.exception("Failed to load memory blob")
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)
