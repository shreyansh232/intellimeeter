from app.core.trace import current_trace_id


def success_response(data):
    return {
        "traceId": current_trace_id.get(),
        "success": True,
        "data": data,
    }