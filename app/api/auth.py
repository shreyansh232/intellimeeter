from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.auth import (
    create_access_token,
    get_password_hash,
    settings,
    verify_password,
)
from app.core.rate_limit import limiter
from app.core.response import success_response
from app.database.db import get_db
from app.database.models import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=SuccessResponse[UserResponse])
@limiter.limit("60/minute")
async def get_me(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get current user information.
    """
    return success_response(current_user)


@router.post("/register", response_model=SuccessResponse[UserResponse])
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Check if user already exists
    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Create new user
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return success_response(user)


@router.post("/login", response_model=SuccessResponse[Token])
@limiter.limit("10/minute")
async def login(
    request: Request,
    login_data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Login endpoint using JSON email and password.
    """
    # Find user
    query = select(User).where(User.email == login_data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return success_response(Token(access_token=access_token, token_type="bearer"))
