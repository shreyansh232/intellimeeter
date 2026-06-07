from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ActionItem, MeetingAnalysis, User
from app.integrations.llm import analyze_transcript
from app.schemas.analysis import MeetingAnalysisLLMResponse
from app.services.meetings import get_meeting


async def analyze_meeting(
    meeting_id: UUID, db: AsyncSession, current_user: User
) -> MeetingAnalysisLLMResponse:

    result = await db.execute(
        select(MeetingAnalysis).where(MeetingAnalysis.meeting_id == meeting_id)
    )

    existing_analysis = result.scalar_one_or_none()

    if existing_analysis:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Meeting has already been analyzed",
        )

    meeting = await get_meeting(
        meeting_id=meeting_id,
        db=db,
        current_user=current_user,
    )

    transcript_analysis = await analyze_transcript(meeting.transcript)

    meeting_analysis = MeetingAnalysis(
        meeting_id=meeting_id,
        summary=[item.model_dump() for item in transcript_analysis.summary],
        decisions=[item.model_dump() for item in transcript_analysis.decisions],
        follow_ups=[item.model_dump() for item in transcript_analysis.follow_ups],
    )
    db.add(meeting_analysis)

    for item in transcript_analysis.action_items:
        action_item = ActionItem(
            meeting_id=meeting.id,
            task=item.task,
            assignee_email=item.assignee,
            due_date=item.due_date,
            citations=[citation.model_dump() for citation in item.citations],
        )

        db.add(action_item)

    try:
        await db.commit()
        await db.refresh(meeting_analysis)
    except Exception:
        await db.rollback()
        raise

    return transcript_analysis
