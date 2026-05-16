from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ParticipantRole(StrEnum):
    DEVELOPER = "developer"
    BA = "ba"
    QA = "qa"


class ParticipantBase(BaseModel):
    plane_user_id: str
    display_name: str
    email: str | None = None
    github_login: str | None = None
    role: ParticipantRole
    active: bool = True


class ParticipantUpsert(ParticipantBase):
    pass


class Participant(ParticipantBase):
    model_config = ConfigDict(from_attributes=True)

    id: str | None = None
    created_at: datetime | None = None
