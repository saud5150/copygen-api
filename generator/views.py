"""API views for copy generation and history retrieval."""

from __future__ import annotations

import logging

from django.utils import timezone
from openai import APIError, APITimeoutError, RateLimitError
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CopyGeneration
from .serializers import (
    GenerationHistorySerializer,
    GenerationRequestSerializer,
    GenerationResponseSerializer,
)
from .services import generate_copy_variations
from .throttling import DailyGenerationThrottle

logger = logging.getLogger(__name__)


class GenerateCopyView(APIView):
    """
    POST /api/v1/generate/

    Accepts product details and returns 3 scored copy variations.
    Rate-limited to 10 requests/day on the free tier.
    """

    throttle_classes = [DailyGenerationThrottle]

    def post(self, request: Request) -> Response:
        serializer = GenerationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            result = generate_copy_variations(
                product_name=data["product_name"],
                product_description=data["product_description"],
                target_audience=data["target_audience"],
                tone=data["tone"],
                platform=data["platform"],
            )
        except RateLimitError:
            return Response(
                {
                    "error": "ai_rate_limit",
                    "message": "AI provider rate limit reached. Please retry in a few seconds.",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except (APITimeoutError, APIError) as exc:
            logger.error("OpenAI API failure: %s", exc)
            return Response(
                {
                    "error": "ai_service_error",
                    "message": "Copy generation service is temporarily unavailable.",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        generation = CopyGeneration.objects.create(
            session_id=data["session_id"],
            product_name=data["product_name"],
            product_description=data["product_description"],
            target_audience=data["target_audience"],
            tone=data["tone"],
            platform=data["platform"],
            variations=result["variations"],
            model_used=result["model_used"],
            prompt_tokens=result["prompt_tokens"],
            completion_tokens=result["completion_tokens"],
            latency_ms=result["latency_ms"],
            ip_address=self._get_client_ip(request),
        )

        logger.info(
            "Generation saved: id=%s session=%s latency=%dms",
            generation.id,
            generation.session_id,
            generation.latency_ms,
        )

        return Response(
            GenerationResponseSerializer(generation).data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _get_client_ip(request: Request) -> str | None:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class GenerationHistoryView(generics.ListAPIView):
    """
    GET /api/v1/history/?session_id=<id>

    Returns paginated generation history for a given session.
    """

    serializer_class = GenerationHistorySerializer

    def get_queryset(self):
        session_id = self.request.query_params.get("session_id")
        if not session_id:
            return CopyGeneration.objects.none()
        return CopyGeneration.objects.filter(session_id=session_id)


class GenerationDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/history/<uuid:pk>/

    Returns full detail for a single generation.
    """

    serializer_class = GenerationResponseSerializer
    queryset = CopyGeneration.objects.all()
    lookup_field = "pk"


class HealthCheckView(APIView):
    """
    GET /api/v1/health/

    Lightweight health probe for uptime monitoring and deploy checks.
    """

    throttle_classes = []

    def get(self, request: Request) -> Response:
        return Response(
            {
                "status": "healthy",
                "service": "copygen-api",
                "timestamp": timezone.now().isoformat(),
            }
        )
