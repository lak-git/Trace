import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.deps import get_plane_client
from app.core.auth import verify_webhook_secret
from app.model.plane import CycleUpdateRequest
from app.service.plane_client import PlaneClient

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/plane",
    tags=["plane"],
    dependencies=[Depends(verify_webhook_secret)],
)

PlaneClientDep = Annotated[PlaneClient, Depends(get_plane_client)]


@router.post("/cycle-update", response_model=None)
async def update_cycle(
    payload: CycleUpdateRequest,
    plane: PlaneClientDep,
) -> dict[str, object] | JSONResponse:
    try:
        result = await plane.append_cycle_description(
            cycle_id=payload.cycle_id,
            summary_text=payload.summary_text,
            project_id=payload.project_id,
        )
        return {"success": True, "data": result.model_dump(mode="json")}
    except Exception as exc:
        logger.exception("Failed to update Plane cycle")
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)
    finally:
        await plane.aclose()
