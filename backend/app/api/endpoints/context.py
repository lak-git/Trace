import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.api.deps import (
    get_blocker_store,
    get_github_client,
    get_memory_store,
    get_participant_store,
    get_plane_client,
)
from app.core.auth import verify_webhook_secret
from app.core.config import Settings, get_settings
from app.model.standup import ContextPrefetchRequest
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
SettingsDep = Annotated[Settings, Depends(get_settings)]


async def _prefetch(
    payload: ContextPrefetchRequest,
    participant_store: ParticipantStoreDep,
    blocker_store: BlockerStoreDep,
    memory_store: MemoryStoreDep,
    plane_client: PlaneClientDep,
    github_client: GitHubClientDep,
    settings: SettingsDep,
) -> dict[str, object] | JSONResponse:
    try:
        compiled, stored_context, missing = await StandupContextService(
            participant_store=participant_store,
            blocker_store=blocker_store,
            memory_store=memory_store,
            plane_client=plane_client,
            github_client=github_client,
            settings=settings,
        ).compile_context(
            project_id=payload.project_id or settings.PLANE_PROJECT_ID,
            cycle_id=payload.cycle_id,
            since=payload.since,
        )

        return {
            "success": True,
            "data": {
                "compiled": compiled.model_dump(mode="json"),
                "stored_context": [item.model_dump(mode="json") for item in stored_context],
                "missing_participants": [item.model_dump(mode="json") for item in missing],
            },
        }
    except Exception as exc:
        logger.exception("Failed to prefetch standup context")
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)


@router.post("/prefetch", response_model=None)
async def prefetch_context_post(
    payload: ContextPrefetchRequest,
    participant_store: ParticipantStoreDep,
    blocker_store: BlockerStoreDep,
    memory_store: MemoryStoreDep,
    plane_client: PlaneClientDep,
    github_client: GitHubClientDep,
    settings: SettingsDep,
) -> dict[str, object] | JSONResponse:
    return await _prefetch(
        payload=payload,
        participant_store=participant_store,
        blocker_store=blocker_store,
        memory_store=memory_store,
        plane_client=plane_client,
        github_client=github_client,
        settings=settings,
    )


@router.get("/prefetch", response_model=None)
async def prefetch_context_get(
    cycle_id: str = Query(...),
    project_id: str | None = Query(default=None),
    participant_store: ParticipantStore = Depends(get_participant_store),
    blocker_store: BlockerStore = Depends(get_blocker_store),
    memory_store: MemoryStore = Depends(get_memory_store),
    plane_client: PlaneClient = Depends(get_plane_client),
    github_client: GitHubClient = Depends(get_github_client),
    settings: Settings = Depends(get_settings),
) -> dict[str, object] | JSONResponse:
    payload = ContextPrefetchRequest(cycle_id=cycle_id, project_id=project_id)
    result = await _prefetch(
        payload=payload,
        participant_store=participant_store,
        blocker_store=blocker_store,
        memory_store=memory_store,
        plane_client=plane_client,
        github_client=github_client,
        settings=settings,
    )
    if isinstance(result, JSONResponse):
        return result
    return {"success": True, "data": result["data"]["stored_context"]}
