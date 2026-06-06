from contextvars import ContextVar

current_trace_id = ContextVar("current_trace_id", default="missing-trace-id")
