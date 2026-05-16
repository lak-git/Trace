import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.api.deps import get_blocker_store
from app.core.auth import verify_webhook_secret
from app.model.blocker import BlockerReport, BlockerResolve, BlockerUpdate
from app.service.blocker_store import BlockerStore

logger = logging.getLogger(__name__)

router = APIRouter(tags=["blockers"], dependencies=[Depends(verify_webhook_secret)])

BlockerStoreDep = Annotated[BlockerStore, Depends(get_blocker_store)]


@router.post("/blocker/report", response_model=None)
async def report_blocker(
    payload: BlockerReport,
    store: BlockerStoreDep,
) -> dict[str, object] | JSONResponse:
    try:
        blocker = await store.report(payload)
        return {"success": True, "data": blocker.model_dump(mode="json")}
    except Exception as exc:
        logger.exception("Failed to report blocker")
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)


@router.post("/blocker/{key}/update", response_model=None)
async def update_blocker(
    key: str,
    payload: BlockerUpdate,
    store: BlockerStoreDep,
) -> dict[str, object] | JSONResponse:
    try:
        blocker = await store.update(key, payload)
        return {"success": True, "data": blocker.model_dump(mode="json")}
    except KeyError as exc:
        return JSONResponse({"success": False, "error": str(exc)}, status_code=404)
    except Exception as exc:
        logger.exception("Failed to update blocker")
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)


@router.post("/blocker/{key}/resolve", response_model=None)
async def resolve_blocker(
    key: str,
    payload: BlockerResolve,
    store: BlockerStoreDep,
) -> dict[str, object] | JSONResponse:
    try:
        blocker = await store.resolve(key, payload)
        return {"success": True, "data": blocker.model_dump(mode="json")}
    except KeyError as exc:
        return JSONResponse({"success": False, "error": str(exc)}, status_code=404)
    except Exception as exc:
        logger.exception("Failed to resolve blocker")
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)


@router.get("/blockers/active", response_model=None)
async def active_blockers(
    store: BlockerStoreDep,
    sprint_id: str | None = Query(default=None),
    participant_id: str | None = Query(default=None),
) -> dict[str, object] | JSONResponse:
    try:
        blockers = await store.list_active(sprint_id=sprint_id, participant_id=participant_id)
        return {"success": True, "data": [item.model_dump(mode="json") for item in blockers]}
    except Exception as exc:
        logger.exception("Failed to list blockers")
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)
