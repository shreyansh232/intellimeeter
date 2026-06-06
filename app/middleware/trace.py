import uuid

from fastapi import Request

from app.core.logger import logger
from app.core.trace import current_trace_id


async def trace_middleware(request: Request, call_next):
    trace_id = (
        request.headers.get("X-Request-ID")
        or request.headers.get("traceId")
        or str(uuid.uuid4())
    )  # request.headers.get("X-Request-ID") isn't needed but for good production practice added it anyways

    token = current_trace_id.set(trace_id)
    
    request.state.trace_id = trace_id

    try:
        logger.info(
            f"trace_id={trace_id} "
            f"method={request.method} "
            f"path={request.url.path} "
            f"status=STARTED"
        )
        response = await call_next(request)
        response.headers["X-Request-ID"] = trace_id
        logger.info(
            f"trace_id={trace_id} "
            f"method={request.method} "
            f"path={request.url.path} "
            f"status={response.status_code}"
        )
        return response
    finally:
        current_trace_id.reset(token)
