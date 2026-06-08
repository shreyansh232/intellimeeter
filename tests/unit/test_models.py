import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Meeting, User


@pytest.mark.asyncio
async def test_user_creation(db_session: AsyncSession):
    user = User(email="test_model@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert isinstance(user.id, uuid.UUID)
    assert user.email == "test_model@example.com"


@pytest.mark.asyncio
async def test_meeting_relationship(db_session: AsyncSession):
    user = User(email="owner@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    meeting = Meeting(
        title="Test Meeting",
        owner_id=user.id,
        participants=["other@example.com"],
        meeting_date=datetime.now(UTC),
        transcript=[{"timestamp": "00:01", "speaker": "User", "text": "Hello"}],
    )
    db_session.add(meeting)
    await db_session.commit()

    # Use selectinload to eagerly load the relationship in async mode
    stmt = select(User).where(User.id == user.id).options(selectinload(User.meetings))
    result = await db_session.execute(stmt)
    user_with_meetings = result.scalar_one()

    assert len(user_with_meetings.meetings) == 1
    assert user_with_meetings.meetings[0].title == "Test Meeting"
