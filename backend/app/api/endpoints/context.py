import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.api.deps import (
    SettingsDep,
    get_blocker_store,
    get_github_client,
    get_memory_store,
    get_participant_store,
    get_plane_client,
)
from app.core.auth import verify_webhook_secret
from app.service.blocker_store import BlockerStore
from app.service.github_client import GitHubClient
from app.service.memory_store import MemoryStore
from app.service.participant_store import ParticipantStore
from app.service.plane_client import PlaneClient
from app.service.standup_context import StandupContextService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/context",
    tags=["context"],
    dependencies=[Depends(verify_webhook_secret)],
)

ParticipantStoreDep = Annotated[ParticipantStore, Depends(get_participant_store)]
BlockerStoreDep = Annotated[BlockerStore, Depends(get_blocker_store)]
MemoryStoreDep = Annotated[MemoryStore, Depends(get_memory_store)]
PlaneClientDep = Annotated[PlaneClient, Depends(get_plane_client)]
GitHubClientDep = Annotated[GitHubClient, Depends(get_github_client)]


@router.get("/prefetch", response_model=None)
async def prefetch_context(
    settings: SettingsDep,
    participant_store: ParticipantStoreDep,
    blocker_store: BlockerStoreDep,
    memory_store: MemoryStoreDep,
    plane: PlaneClientDep,
    github: GitHubClientDep,
    cycle_id: str = Query(...),
    project_id: str | None = Query(default=None),
    since: datetime | None = Query(default=None),
) -> dict[str, object] | JSONResponse:
    pid = project_id or settings.PLANE_PROJECT_ID
    service = StandupContextService(
        participant_store=participant_store,
        blocker_store=blocker_store,
        memory_store=memory_store,
        plane_client=plane,
        github_client=github,
    )
    try:
        compiled, stored, missing = await service.compile_context(
            project_id=pid,
            cycle_id=cycle_id,
            since=since,
        )
        return {
            "success": True,
            "data": {
                "compiled": compiled.model_dump(mode="json"),
                "stored_context": [item.model_dump(mode="json") for item in stored],
                "missing_participants": [item.model_dump(mode="json") for item in missing],
            },
        }
    except Exception as exc:
        logger.exception("Failed to prefetch standup context")
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)
    finally:
        await plane.aclose()
        await github.aclose()
