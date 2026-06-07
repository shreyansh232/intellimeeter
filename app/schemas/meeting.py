import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Transcript(BaseModel):
    timestamp: str
    speaker: str
    text: str


class MeetingBase(BaseModel):
    title: str
    meeting_date: datetime
    participants: list[EmailStr] = Field(min_length=1)
    transcript: list[Transcript] = Field(min_length=1)


class MeetingCreate(MeetingBase):
    pass


class MeetingResponse(MeetingBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
