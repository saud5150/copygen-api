"""Groq API integration layer (OpenAI-compatible).

Handles the API call, response parsing, error recovery, and token tracking.
Falls back to a structured error if the API response isn't valid JSON.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from django.conf import settings
from openai import OpenAI, APIError, APITimeoutError, RateLimitError

from .prompt_engine import PromptEngine
from .scoring import PersuasionScorer

logger = logging.getLogger(__name__)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL,
            timeout=30.0,
            max_retries=2,
        )
    return _client


def generate_copy_variations(
    product_name: str,
    product_description: str,
    target_audience: str,
    tone: str,
    platform: str,
) -> dict[str, Any]:
    """
    Call the Groq API and return scored variations.

    Returns:
        {
            "variations": [{"copy": str, "persuasion_score": float}, ...],
            "model_used": str,
            "prompt_tokens": int,
            "completion_tokens": int,
            "latency_ms": int,
        }
    """
    client = _get_client()
    user_prompt = PromptEngine.build_user_prompt(
        product_name=product_name,
        product_description=product_description,
        target_audience=target_audience,
        tone=tone,
        platform=platform,
    )

    logger.info(
        "Generating copy: product=%s platform=%s tone=%s",
        product_name,
        platform,
        tone,
    )

    start = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": PromptEngine.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=settings.GROQ_MAX_TOKENS,
            temperature=settings.GROQ_TEMPERATURE,
            response_format={"type": "json_object"},
        )
    except RateLimitError:
        logger.error("Groq rate limit hit")
        raise
    except APITimeoutError:
        logger.error("Groq request timed out")
        raise
    except APIError as exc:
        logger.error("Groq API error: %s", exc)
        raise

    latency_ms = int((time.perf_counter() - start) * 1000)

    raw_content = response.choices[0].message.content or ""
    prompt_tokens = response.usage.prompt_tokens if response.usage else 0
    completion_tokens = response.usage.completion_tokens if response.usage else 0

    logger.info(
        "Groq responded: tokens=%d+%d latency=%dms",
        prompt_tokens,
        completion_tokens,
        latency_ms,
    )

    variations = _parse_variations(raw_content)
    scored = _score_variations(variations, platform)

    return {
        "variations": scored,
        "model_used": settings.GROQ_MODEL,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "latency_ms": latency_ms,
    }


def _parse_variations(raw: str) -> list[str]:
    """Extract copy strings from the model's JSON output."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Failed to parse JSON response, attempting extraction")
        return _fallback_extract(raw)

    # Handle both {"variations": [...]} and direct [...]
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("variations", data.get("copies", []))
        if not items:
            for v in data.values():
                if isinstance(v, list):
                    items = v
                    break
    else:
        return _fallback_extract(raw)

    copies = []
    for item in items:
        if isinstance(item, str):
            copies.append(item)
        elif isinstance(item, dict):
            text = item.get("copy", item.get("text", item.get("content", "")))
            if text:
                copies.append(str(text))

    if not copies:
        return _fallback_extract(raw)

    return copies[:3]


def _fallback_extract(raw: str) -> list[str]:
    """Last-resort: split on numbered patterns."""
    import re

    parts = re.split(r"\n\d+[\.\)]\s*", raw)
    parts = [p.strip().strip('"') for p in parts if p.strip()]
    if parts:
        return parts[:3]
    return [raw.strip()] if raw.strip() else ["Copy generation failed — please retry."]


def _score_variations(copies: list[str], platform: str) -> list[dict[str, Any]]:
    return [
        {
            "copy": text,
            "persuasion_score": PersuasionScorer.score(text, platform),
        }
        for text in copies
    ]
