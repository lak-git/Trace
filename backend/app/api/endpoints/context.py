import logging

from fastapi import APIRouter, Depends, Query

from app.core.auth import verify_webhook_secret

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/context",
    tags=["context"],
    dependencies=[Depends(verify_webhook_secret)],
)

MOCK_CONTEXT_DATA = [
    {
        "sprint_id": "sprint-7",
        "participant_id": "usr_alice_biometrics",
        "commits": [
            {
                "sha": "commit1",
                "message": "feat(biometrics): add FaceID enrollment flow",
                "url": "github.com/repo/financeflow/commits/1",
                "date": "2026-05-16T00:00:00Z",
            },
            {
                "sha": "commit2",
                "message": "fix(biometrics): handle cancelled auth",
                "url": "github.com/repo/financeflow/commits/2",
                "date": "2026-05-16T00:00:00Z",
            },
        ],
        "blockers": [],
        "last_summary": "Alice successfully completed the baseline biometric encryption wrapper yesterday. No blockers reported.",
        "compiled_at": "2026-05-16T09:45:00Z",
    },
    {
        "sprint_id": "sprint-7",
        "participant_id": "usr_bob_payment",
        "commits": [
            {
                "sha": "commit3",
                "message": "fix(payment-timeout): add circuit breaker",
                "url": "github.com/repo/financeflow/commits/3",
                "date": "2026-05-16T00:00:00Z",
            },
            {
                "sha": "commit4",
                "message": "fix(payment-timeout): flaky test WIP",
                "url": "github.com/repo/financeflow/commits/4",
                "date": "2026-05-16T00:00:00Z",
            },
        ],
        "blockers": [
            {
                "key": "bob-ci-flakiness",
                "participant_id": "usr_bob_payment",
                "sprint_id": "sprint-7",
                "description": "CI test flakiness on payment endpoints impacting deployment",
                "status": "active",
                "source": "standup",
                "github_url": None,
                "last_update": None,
                "created_at": "2026-05-15T10:00:00Z",
                "updated_at": "2026-05-16T08:30:00Z",
                "resolved_at": None,
            },
        ],
        "last_summary": "Bob mentioned having environment orchestration setup errors with the local testing framework.",
        "compiled_at": "2026-05-16T09:45:00Z",
    },
    {
        "sprint_id": "sprint-7",
        "participant_id": "usr_carol_dashboard",
        "commits": [
            {
                "sha": "commit5",
                "message": "feat(dashboard): transaction list component",
                "url": "github.com/repo/financeflow/commits/5",
                "date": "2026-05-16T00:00:00Z",
            },
        ],
        "blockers": [],
        "last_summary": "Carol was working through UI responsiveness issues for the dashboard layouts on mobile screens.",
        "compiled_at": "2026-05-16T09:45:00Z",
    },
]


@router.get("/prefetch", response_model=None)
async def prefetch_context(
    cycle_id: str = Query(...),
    project_id: str | None = Query(default=None),
) -> dict[str, object]:
    return {"success": True, "data": MOCK_CONTEXT_DATA}
