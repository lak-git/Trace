from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from app.core.config import Settings
from app.model.participant import Participant, ParticipantRole
from app.model.standup import (
    CompiledContext,
    GitCommit,
    ParticipantContext,
    StandupContext,
    StoredCommit,
)
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
        settings: Settings,
    ) -> None:
        self._participant_store = participant_store
        self._blocker_store = blocker_store
        self._memory_store = memory_store
        self._plane_client = plane_client
        self._github_client = github_client
        self._settings = settings

    def _standup_window(self, now: datetime | None = None) -> tuple[datetime, datetime]:
        now_utc = now or datetime.now(UTC)
        tz = ZoneInfo(self._settings.STANDUP_TIMEZONE)
        localized_now = now_utc.astimezone(tz)
        current_standup = localized_now.replace(hour=9, minute=0, second=0, microsecond=0)
        previous_standup = current_standup - timedelta(days=1)
        return previous_standup.astimezone(UTC), current_standup.astimezone(UTC)

    @staticmethod
    def _strip_transient_commit_fields(commits: list[GitCommit]) -> list[GitCommit]:
        sanitized: list[GitCommit] = []
        for commit in commits:
            sanitized.append(
                GitCommit(
                    sha=commit.sha,
                    message=commit.message,
                    url=commit.url,
                    date=commit.date,
                    author_name=commit.author_name,
                    author_email=commit.author_email,
                ),
            )
        return sanitized

    @staticmethod
    def _prefetch_commit_rows(commits: list[GitCommit]) -> list[StoredCommit]:
        rows: list[StoredCommit] = []
        for commit in StandupContextService._strip_transient_commit_fields(commits):
            rows.append(
                StoredCommit(
                    sha=commit.sha,
                    message=(commit.message or "").split("\n", maxsplit=1)[0].strip() or None,
                    url=commit.url,
                    date=commit.date,
                    summary=None,
                ),
            )
        return rows

    async def compile_context(
        self,
        project_id: str,
        cycle_id: str,
        since: datetime | None = None,
    ) -> tuple[CompiledContext, list[StandupContext], list[Participant]]:
        sprint_id = cycle_id
        window_start, window_end = self._standup_window()
        from_time = since or window_start
        plane_members = await self._plane_client.list_project_members(project_id=project_id)
        context_rows: list[StandupContext] = []
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
            has_recent_commits = False
            if participant.role == ParticipantRole.DEVELOPER:
                commits = await self._github_client.commits_since(
                    github_login=participant.github_login,
                    email=participant.email,
                    since=from_time,
                )
                commits = [
                    commit
                    for commit in commits
                    if commit.date is not None and from_time <= commit.date < window_end
                ]
                has_recent_commits = len(commits) > 0
                if not has_recent_commits:
                    latest_commit = await self._github_client.latest_commit(
                        github_login=participant.github_login,
                        email=participant.email,
                    )
                    commits = [latest_commit] if latest_commit else []

            context_rows.append(
                StandupContext(
                    sprint_id=sprint_id,
                    participant_id=participant.plane_user_id,
                    commits=self._prefetch_commit_rows(commits),
                    blockers=blockers,
                    last_summary=last_summary,
                ),
            )
            participant_contexts.append(
                ParticipantContext(
                    participant_id=participant.plane_user_id,
                    display_name=participant.display_name,
                    role=participant.role,
                    commits=commits,
                    has_recent_commits=has_recent_commits,
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
            context_rows,
            missing_participants,
        )
