from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ActionItem, Meeting, User
from app.schemas.action_item import ActionItemCreate, ActionItemStatus
from app.services.meetings import get_meeting


async def create_action_item(
    data: ActionItemCreate, db: AsyncSession, current_user: User
) -> ActionItem:
    await get_meeting(
        meeting_id=data.meeting_id,
        db=db,
        current_user=current_user,
    )

    action_item = ActionItem(
        meeting_id=data.meeting_id,
        task=data.task,
        assignee_email=data.assignee_email,
        due_date=data.due_date,
        status=ActionItemStatus.PENDING,
    )

    db.add(action_item)

    try:
        await db.commit()
        await db.refresh(action_item)

    except Exception:
        await db.rollback()
        raise
    return action_item


async def update_action_item_status(
    action_item_id: UUID,
    new_status: ActionItemStatus,
    db: AsyncSession,
    current_user: User,
) -> ActionItem:
    result = await db.execute(
        select(ActionItem)
        .join(Meeting, ActionItem.meeting_id == Meeting.id)
        .where(
            ActionItem.id == action_item_id,
            Meeting.owner_id == current_user.id,
        )
    )

    action_item = result.scalar_one_or_none()

    if action_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action item not found",
        )

    action_item.status = new_status

    try:
        await db.commit()
        await db.refresh(action_item)
    except Exception:
        await db.rollback()
        raise

    return action_item


async def get_action_items(
    db: AsyncSession,
    current_user: User,
    limit: int = 10,
    offset: int = 0,
    status: ActionItemStatus | None = None,
    assignee_email: str | None = None,
    meeting_id: UUID | None = None,
):
    query = (
        select(ActionItem)
        .join(Meeting, ActionItem.meeting_id == Meeting.id)
        .where(Meeting.owner_id == current_user.id)
    )

    if status:
        query = query.where(ActionItem.status == status)

    if assignee_email:
        query = query.where(ActionItem.assignee_email == assignee_email)

    if meeting_id:
        query = query.where(ActionItem.meeting_id == meeting_id)

    query = query.limit(limit).offset(offset)

    result = await db.execute(query)

    return result.scalars().all()


async def get_overdue_action_items(
    db: AsyncSession,
    current_user: User,
):
    result = await db.execute(
        select(ActionItem)
        .join(Meeting, ActionItem.meeting_id == Meeting.id)
        .where(
            Meeting.owner_id == current_user.id,
            ActionItem.status != "COMPLETED",
            ActionItem.due_date < datetime.now(UTC),
        )
    )

    return result.scalars().all()


async def get_all_overdue_action_items(
    db: AsyncSession,
):
    result = await db.execute(
        select(ActionItem)
        .where(
            ActionItem.status != "COMPLETED",
            ActionItem.due_date < datetime.now(UTC),
        )
    )

    return result.scalars().all()