from uuid import UUID

from fastapi import APIRouter, Depends, status
from app.services.analysis import analyze_meeting
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.response import success_response
from app.database.db import get_db
from app.database.models import User
from app.schemas.meeting import MeetingCreate, MeetingResponse
from app.services.meetings import create_meeting, get_meeting, list_meetings

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_meeting_route(
    data: MeetingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = await create_meeting(data=data, db=db, current_user=current_user)

    meeting_response = MeetingResponse.model_validate(meeting)

    return success_response(meeting_response)


@router.get("/{meeting_id}")
async def get_meeting_route(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = await get_meeting(meeting_id=meeting_id, db=db, current_user=current_user)

    meeting_response = MeetingResponse.model_validate(meeting)

    return success_response(meeting_response)


@router.get("")
async def list_meetings_route(
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meetings = await list_meetings(
        limit=limit,
        offset=offset,
        db=db,
        current_user=current_user,
    )

    return success_response(
        [MeetingResponse.model_validate(meeting) for meeting in meetings]
    )


@router.post("/{meeting_id}/analyze")
async def analyze_meeting_route(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = await analyze_meeting(meeting_id=meeting_id, db=db, current_user=current_user)

    return success_response(analysis)
