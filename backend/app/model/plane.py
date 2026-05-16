from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PlaneMember(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    display_name: str | None = None
    email: str | None = None


class PlaneCycle(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    name: str | None = None
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class PlaneIssue(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    name: str | None = None
    description: str | None = None
    assignees: list[str] = Field(default_factory=list)
    state: str | None = None


class CycleUpdateRequest(BaseModel):
    project_id: str | None = None
    cycle_id: str
    summary_text: str


class CycleUpdateResult(BaseModel):
    cycle_id: str
    description: str
    raw: dict[str, Any]
