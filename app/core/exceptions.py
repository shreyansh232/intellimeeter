from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logger import logger
from app.core.trace import current_trace_id


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    trace_id = getattr(
        request.state,
        "trace_id",
        current_trace_id.get(),
    )

    logger.error(
        f"trace_id={trace_id} "
        f"method={request.method} "
        f"path={request.url.path} "
        f"validation_error={exc.errors()}"
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "traceId": trace_id,
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(exc.errors()),
            },
        },
    )


async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    trace_id = getattr(
        request.state,
        "trace_id",
        current_trace_id.get(),
    )

    logger.exception(
        f"trace_id={trace_id} method={request.method} path={request.url.path}"
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "traceId": trace_id,
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Something went wrong",
            },
        },
    )
