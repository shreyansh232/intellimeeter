from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.rate_limit import limiter
from app.core.response import success_response
from app.database.db import get_db
from app.database.models import User
from app.schemas.action_item import (
    ActionItemCreate,
    ActionItemStatus,
    ActionItemStatusUpdate,
)
from app.services.action_items import (
    create_action_item,
    get_action_items,
    get_overdue_action_items,
    update_action_item_status,
)

router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("")
@limiter.limit("30/minute")
async def create_action_item_route(
    request: Request,
    data: ActionItemCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    action_item = await create_action_item(
        data=data,
        db=db,
        current_user=current_user,
    )

    return success_response(action_item)


@router.patch("/{action_item_id}/status")
@limiter.limit("60/minute")
async def update_action_item_status_route(
    request: Request,
    action_item_id: UUID,
    data: ActionItemStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    action_item = await update_action_item_status(
        action_item_id=action_item_id,
        new_status=data.status,
        db=db,
        current_user=current_user,
    )

    return success_response(action_item)


@router.get("")
@limiter.limit("60/minute")
async def get_action_items_route(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: ActionItemStatus | None = None,
    assignee_email: str | None = None,
    meeting_id: UUID | None = None,
):
    action_items = await get_action_items(
        db=db,
        current_user=current_user,
        limit=limit,
        offset=offset,
        status=status,
        assignee_email=assignee_email,
        meeting_id=meeting_id,
    )

    return success_response(action_items)


@router.get("/overdue")
@limiter.limit("60/minute")
async def get_overdue_action_items_route(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    action_items = await get_overdue_action_items(
        db=db,
        current_user=current_user,
    )

    return success_response(action_items)
