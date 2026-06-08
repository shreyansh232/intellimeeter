from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import router as api_router
from app.api.deps import get_current_user
from app.core.exceptions import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.rate_limit import limiter
from app.core.response import success_response
from app.database import models  # noqa: F401
from app.database.db import Base, engine, get_db
from app.jobs.scheduler import scheduler
from app.middleware.trace import trace_middleware
from app.services.reminders import process_overdue_reminders


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit exceeded: {exc.detail}",
            },
        },
    )


app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

app.middleware("http")(trace_middleware)

app.exception_handler(RequestValidationError)(validation_exception_handler)
app.exception_handler(Exception)(global_exception_handler)
app.exception_handler(HTTPException)(http_exception_handler)


@app.get("/health")
async def health_check():
    return success_response({"status": "UP"})


@app.post("/run")
@limiter.limit("10/minute")
async def run_reminders(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    await process_overdue_reminders(
        db=db,
        current_user=current_user,
    )

    return success_response({"success": True})
