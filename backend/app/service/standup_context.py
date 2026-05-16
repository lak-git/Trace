from datetime import UTC, datetime, timedelta

from app.model.participant import Participant, ParticipantRole
from app.model.standup import CompiledContext, ParticipantContext, StandupContext
from app.service.blocker_store import BlockerStore
from app.service.github_client import GitHubClient
from app.service.memory_store import MemoryStore
from app.service.participant_store import ParticipantStore
from app.service.plane_client import PlaneClient


class StandupContextService:
    def __init__(
        self,
        participant_store: ParticipantStore,
        blocker_store: BlockerStore,
        memory_store: MemoryStore,
        plane_client: PlaneClient,
        github_client: GitHubClient,
    ) -> None:
        self._participant_store = participant_store
        self._blocker_store = blocker_store
        self._memory_store = memory_store
        self._plane_client = plane_client
        self._github_client = github_client

    async def compile_context(
        self,
        project_id: str,
        cycle_id: str,
        since: datetime | None = None,
    ) -> tuple[CompiledContext, list[StandupContext], list[Participant]]:
        sprint_id = cycle_id
        from_time = since or (datetime.now(UTC) - timedelta(days=1))
        plane_members = await self._plane_client.list_project_members(project_id=project_id)
        stored_context: list[StandupContext] = []
        participant_contexts: list[ParticipantContext] = []
        missing_participants: list[Participant] = []

        for member in plane_members:
            participant = await self._participant_store.get_by_plane_user_id(member.id)
            if participant is None:
                missing_participants.append(
                    Participant(
                        plane_user_id=member.id,
                        display_name=member.display_name or member.email or member.id,
                        email=member.email,
                        github_login=None,
                        role=ParticipantRole.DEVELOPER,
                        active=False,
                    ),
                )
                continue

            blockers = await self._blocker_store.list_active(
                sprint_id=sprint_id,
                participant_id=participant.plane_user_id,
            )
            last_summary = await self._memory_store.latest_summary(
                participant_id=participant.plane_user_id,
                sprint_id=sprint_id,
            )
            commits = []
            if participant.role == ParticipantRole.DEVELOPER:
                commits = await self._github_client.commits_since(
                    github_login=participant.github_login,
                    email=participant.email,
                    since=from_time,
                )

            context = StandupContext(
                sprint_id=sprint_id,
                participant_id=participant.plane_user_id,
                commits=commits,
                blockers=blockers,
                last_summary=last_summary,
            )
            stored = await self._memory_store.upsert_context(context)
            stored_context.append(stored)
            participant_contexts.append(
                ParticipantContext(
                    participant_id=participant.plane_user_id,
                    display_name=participant.display_name,
                    role=participant.role,
                    commits=commits,
                    active_blockers=blockers,
                    last_summary=last_summary,
                ),
            )

        return (
            CompiledContext(
                sprint_id=sprint_id,
                project_id=project_id,
                cycle_id=cycle_id,
                participants=participant_contexts,
            ),
            stored_context,
            missing_participants,
        )
