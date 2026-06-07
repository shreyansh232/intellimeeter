# Create a new meeting - POST
# Fetch a meeintg - GET
# Fetch all meetings with limit offset pagination - GET


from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Meeting, User
from app.schemas.meeting import MeetingCreate


async def create_meeting(
    data: MeetingCreate, db: AsyncSession, current_user: User
) -> Meeting:
    if not data.transcript:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Transcript can't be empty"
        )

    if not data.participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participants can't be empty",
        )

    meeting = Meeting(
        owner_id=current_user.id,
        title=data.title,
        participants=data.participants,
        transcript=[
            {
                "timestamp": entry.timestamp,
                "speaker": entry.speaker,
                "text": entry.text,
            }
            for entry in data.transcript
        ],
        meeting_date=data.meeting_date,
    )

    db.add(meeting)

    try:
        await db.commit()
        await db.refresh(meeting)

    except Exception:
        await db.rollback()
        raise

    return meeting


async def get_meeting(
    meeting_id: UUID, db: AsyncSession, current_user: User
) -> Meeting:
    result = await db.execute(
        select(Meeting).where(
            Meeting.id == meeting_id,
            Meeting.owner_id == current_user.id,
        )
    )

    meeting = result.scalar_one_or_none()

    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found"
        )
    return meeting


async def list_meetings(
    limit: int,
    offset: int,
    db: AsyncSession,
    current_user: User,
) -> list[Meeting]:
    result = await db.execute(
        select(Meeting)
        .where(Meeting.owner_id == current_user.id)
        .order_by(Meeting.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    return result.scalars().all()
