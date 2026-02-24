"""Request logging middleware for observability."""

from __future__ import annotations

import logging
import time

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("generator")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.perf_counter()
        response = self.get_response(request)
        duration_ms = int((time.perf_counter() - start) * 1000)

        if request.path.startswith("/api/"):
            logger.info(
                "%s %s %d %dms",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
            )

        return response
