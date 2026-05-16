from datetime import date, datetime
from enum import IntEnum, StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.model.blocker import Blocker
from app.model.participant import Participant


class MemoryImportance(IntEnum):
    ROUTINE = 1
    IMPORTANT = 2
    BLOCKER = 3


class MemoryUpsert(BaseModel):
    participant_id: str
    sprint_id: str
    standup_date: date
    summary: str
    importance: int = Field(default=1, ge=1, le=3)
    stale: bool = False


class AgentMemory(MemoryUpsert):
    model_config = ConfigDict(from_attributes=True)

    id: str | None = None
    created_at: datetime | None = None


class MemoryCompactRequest(BaseModel):
    participant_id: str | None = None
    sprint_id: str
    transcript: str = Field(min_length=1)


class MemoryCompactResponse(BaseModel):
    summary: str
    importance: int = Field(default=1, ge=1, le=3)


class SprintMemoryCategory(StrEnum):
    GOAL = "goal"
    DECISION = "decision"
    BOUNDARY = "boundary"
    NOTE = "note"


class SprintMemoryFact(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | None = None
    sprint_id: str
    key_fact: str
    category: SprintMemoryCategory = SprintMemoryCategory.NOTE
    created_at: datetime | None = None


class CompactedSprintMemory(BaseModel):
    sprint_id: str
    participants: list[Participant] = Field(default_factory=list)
    memory: list[AgentMemory] = Field(default_factory=list)
    blockers: list[Blocker] = Field(default_factory=list)
    sprint_facts: list[SprintMemoryFact] = Field(default_factory=list)
