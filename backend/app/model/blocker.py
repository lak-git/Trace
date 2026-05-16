from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class BlockerStatus(StrEnum):
    ACTIVE = "active"
    RESOLVED = "resolved"


class BlockerSource(StrEnum):
    MANUAL = "manual"
    GITHUB_COMMIT = "github_commit"
    STANDUP = "standup"


class BlockerReport(BaseModel):
    participant_id: str
    description: str
    sprint_id: str | None = None
    key: str | None = None
    source: BlockerSource = BlockerSource.MANUAL
    github_url: str | None = None
    last_update: str | None = None


class BlockerUpdate(BaseModel):
    last_update: str = Field(min_length=1)
    github_url: str | None = None


class BlockerResolve(BaseModel):
    resolution: str | None = None
    github_url: str | None = None


class Blocker(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | None = None
    key: str
    participant_id: str
    sprint_id: str | None = None
    description: str
    status: BlockerStatus = BlockerStatus.ACTIVE
    source: BlockerSource = BlockerSource.MANUAL
    github_url: str | None = None
    last_update: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    resolved_at: datetime | None = None
