from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api import router as api_router
from app.core.exceptions import (
    global_exception_handler,
    validation_exception_handler,
)
from app.database import models  # noqa: F401
from app.database.db import Base, engine
from app.middleware.trace import trace_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
app.middleware("http")(trace_middleware)
app.exception_handler(RequestValidationError)(validation_exception_handler)

app.exception_handler(Exception)(global_exception_handler)


@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)
