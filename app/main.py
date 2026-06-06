from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)
