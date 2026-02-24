"""Custom exception handling for the API."""

from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):
        response = Response(
            {
                "error": "rate_limit_exceeded",
                "message": (
                    f"Free tier limit reached. Try again in {exc.wait:.0f} seconds."
                    if exc.wait
                    else "Free tier limit reached. Try again later."
                ),
                "retry_after_seconds": int(exc.wait) if exc.wait else None,
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )
    elif response is not None:
        response.data = {
            "error": _error_code(response.status_code),
            "message": _flatten_errors(response.data),
            "status_code": response.status_code,
        }
    else:
        logger.exception("Unhandled exception in view: %s", exc)
        response = Response(
            {
                "error": "internal_error",
                "message": "An unexpected error occurred. Please try again later.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def _error_code(status_code: int) -> str:
    mapping = {
        400: "validation_error",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        429: "rate_limit_exceeded",
    }
    return mapping.get(status_code, "error")


def _flatten_errors(data) -> str | dict:
    """Flatten DRF's nested error dicts into readable messages."""
    if isinstance(data, str):
        return data
    if isinstance(data, list):
        return "; ".join(str(item) for item in data)
    if isinstance(data, dict):
        parts = []
        for field, errors in data.items():
            if field == "detail":
                return str(errors)
            if isinstance(errors, list):
                parts.append(f"{field}: {'; '.join(str(e) for e in errors)}")
            else:
                parts.append(f"{field}: {errors}")
        return "; ".join(parts) if parts else str(data)
    return str(data)
