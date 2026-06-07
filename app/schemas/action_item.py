from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActionItemStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class ActionItemBase(BaseModel):
    meeting_id: UUID
    task: str
    assignee_email: str | None
    due_date: datetime | None


class ActionItemCreate(ActionItemBase):
    pass


class ActionItemStatusUpdate(BaseModel):
    status: ActionItemStatus


class ActionItemResponse(ActionItemBase):
    id: UUID
    created_at: datetime
    status: ActionItemStatus

    model_config = ConfigDict(from_attributes=True)
