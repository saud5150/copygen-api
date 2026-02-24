"""Persuasion scoring heuristic.

Computes a 0-100 score based on empirically weighted copywriting signals:
  - CTA presence and strength
  - Emotional / power-word density
  - Optimal length for the target platform
  - Readability (sentence length variance)
  - Urgency cues
  - Social proof indicators
"""

from __future__ import annotations

import math
import re

STRONG_CTAS = {
    "buy now", "shop now", "get started", "sign up", "subscribe",
    "download", "try free", "claim your", "start your", "join now",
    "book now", "learn more", "get yours", "order now", "grab yours",
    "reserve your", "unlock", "discover", "apply now", "start free",
}

POWER_WORDS = {
    "free", "new", "proven", "guaranteed", "exclusive", "limited",
    "instant", "revolutionary", "breakthrough", "secret", "powerful",
    "ultimate", "premium", "transform", "unleash", "effortless",
    "remarkable", "stunning", "unbelievable", "incredible", "essential",
    "massive", "epic", "game-changing", "dominant",
}

EMOTIONAL_WORDS = {
    "love", "hate", "fear", "joy", "trust", "surprise", "amazing",
    "thrilled", "devastating", "exciting", "inspiring", "passionate",
    "obsessed", "dreaming", "craving", "confident", "proud", "bold",
    "grateful", "delighted", "anxious", "worried",
}

URGENCY_WORDS = {
    "now", "today", "hurry", "limited", "last chance", "don't miss",
    "ending soon", "only", "deadline", "before it's gone", "act fast",
    "running out", "final", "expires", "countdown",
}

SOCIAL_PROOF_PATTERNS = [
    r"\d+[,.]?\d*\s*(customers|users|people|businesses|brands)",
    r"trusted by",
    r"as seen",
    r"rated",
    r"\d+\s*stars?",
    r"#1",
    r"best[\s-]selling",
]

OPTIMAL_LENGTHS: dict[str, tuple[int, int]] = {
    "instagram": (100, 800),
    "linkedin": (150, 1000),
    "google_ad": (30, 210),
    "email_subject": (20, 60),
    "facebook": (40, 200),
    "twitter": (50, 280),
}


class PersuasionScorer:
    """Scores a piece of copy on a 0-100 persuasion heuristic."""

    @classmethod
    def score(cls, copy_text: str, platform: str) -> float:
        text_lower = copy_text.lower()
        words = text_lower.split()
        word_count = len(words)

        if word_count == 0:
            return 0.0

        components = {
            "cta": cls._cta_score(text_lower),
            "power_words": cls._keyword_density_score(words, POWER_WORDS),
            "emotional": cls._keyword_density_score(words, EMOTIONAL_WORDS),
            "urgency": cls._keyword_density_score(words, URGENCY_WORDS),
            "length": cls._length_score(len(copy_text), platform),
            "readability": cls._readability_score(copy_text),
            "social_proof": cls._social_proof_score(text_lower),
        }

        weights = {
            "cta": 0.25,
            "power_words": 0.15,
            "emotional": 0.15,
            "urgency": 0.10,
            "length": 0.15,
            "readability": 0.10,
            "social_proof": 0.10,
        }

        raw = sum(components[k] * weights[k] for k in weights)
        return round(min(max(raw, 0), 100), 1)

    @staticmethod
    def _cta_score(text_lower: str) -> float:
        """0-100 based on CTA presence. Strong CTAs score higher."""
        matches = sum(1 for cta in STRONG_CTAS if cta in text_lower)
        if matches >= 2:
            return 100.0
        if matches == 1:
            return 80.0
        # Weak CTA detection: imperative verbs at sentence boundaries
        weak_cta = re.search(
            r"(click|tap|visit|check out|see|explore|find|go to)\b", text_lower
        )
        return 45.0 if weak_cta else 0.0

    @staticmethod
    def _keyword_density_score(words: list[str], keyword_set: set[str]) -> float:
        """Score based on density of target keywords, with diminishing returns."""
        if not words:
            return 0.0
        hits = sum(1 for w in words if w.strip(".,!?;:\"'()") in keyword_set)
        density = hits / len(words)
        # Sweet spot: 2-6% density. Penalize keyword stuffing.
        if density < 0.01:
            return density * 3000  # linear ramp to ~30
        if density <= 0.06:
            return 50 + (density - 0.01) * 1000  # ramp to 100
        return max(100 - (density - 0.06) * 800, 40)  # diminishing returns

    @staticmethod
    def _length_score(char_count: int, platform: str) -> float:
        """Scores how well the copy length matches platform norms."""
        low, high = OPTIMAL_LENGTHS.get(platform, (50, 500))
        if low <= char_count <= high:
            return 100.0
        if char_count < low:
            return max((char_count / low) * 80, 0)
        overshoot = (char_count - high) / high
        return max(100 - overshoot * 150, 10)

    @staticmethod
    def _readability_score(text: str) -> float:
        """Rewards varied sentence lengths (a sign of engaging rhythm)."""
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) < 2:
            return 50.0
        lengths = [len(s.split()) for s in sentences]
        mean = sum(lengths) / len(lengths)
        if mean == 0:
            return 30.0
        variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
        cv = math.sqrt(variance) / mean  # coefficient of variation
        # CV between 0.3 and 0.8 indicates good variety
        if 0.3 <= cv <= 0.8:
            return 100.0
        if cv < 0.3:
            return 50 + cv * 166
        return max(100 - (cv - 0.8) * 100, 30)

    @staticmethod
    def _social_proof_score(text_lower: str) -> float:
        matches = sum(
            1 for pattern in SOCIAL_PROOF_PATTERNS if re.search(pattern, text_lower)
        )
        return min(matches * 40, 100.0)
