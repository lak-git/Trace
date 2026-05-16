from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.model.blocker import Blocker
from app.model.participant import Participant, ParticipantRole


class GitCommit(BaseModel):
    sha: str
    message: str
    url: str | None = None
    date: datetime | None = None
    author_name: str | None = None
    author_email: str | None = None


class StandupContext(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | None = None
    sprint_id: str
    participant_id: str
    commits: list[GitCommit] = Field(default_factory=list)
    blockers: list[Blocker] = Field(default_factory=list)
    last_summary: str | None = None
    compiled_at: datetime | None = None


class ParticipantContext(BaseModel):
    participant_id: str
    display_name: str
    role: ParticipantRole
    commits: list[GitCommit] = Field(default_factory=list)
    active_blockers: list[Blocker] = Field(default_factory=list)
    last_summary: str | None = None


class CompiledContext(BaseModel):
    sprint_id: str
    project_id: str
    cycle_id: str
    participants: list[ParticipantContext] = Field(default_factory=list)


class ContextPrefetchRequest(BaseModel):
    project_id: str | None = None
    cycle_id: str
    since: datetime | None = None


class ContextPrefetchResult(BaseModel):
    compiled: CompiledContext
    stored_context: list[StandupContext]
    missing_participants: list[Participant] = Field(default_factory=list)
