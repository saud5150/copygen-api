"""Prompt construction for the copy generation pipeline.

The system prompt establishes the AI's persona and constraints.
The user prompt is dynamically assembled from validated request fields.
"""

from __future__ import annotations

PLATFORM_GUIDELINES: dict[str, str] = {
    "instagram": (
        "Max 2200 characters. Lead with a hook in the first line. "
        "Use line breaks for readability. Include 2-3 relevant hashtag suggestions. "
        "Emojis are acceptable if they match the tone."
    ),
    "linkedin": (
        "Professional register. Open with a bold statement or statistic. "
        "Keep paragraphs to 1-2 sentences. End with a clear CTA or question "
        "to drive engagement. No hashtags in the body; suggest 3 at the end."
    ),
    "google_ad": (
        "Headline: max 30 characters. Description line 1: max 90 characters. "
        "Description line 2: max 90 characters. Be extremely concise. "
        "Include the primary keyword naturally. Strong CTA verb required."
    ),
    "email_subject": (
        "Max 60 characters including spaces. Create curiosity or urgency. "
        "Avoid spam-trigger words (free, guarantee, act now). "
        "Personalization tokens like {first_name} are allowed."
    ),
    "facebook": (
        "Optimal length: 40-80 characters for highest engagement. "
        "Conversational tone. Ask questions to boost comments. "
        "Include a clear CTA linking to the next step."
    ),
    "twitter": (
        "Max 280 characters. Punchy and direct. "
        "One core idea per tweet. CTA or hook at the start."
    ),
}

TONE_MODIFIERS: dict[str, str] = {
    "professional": "Use a polished, authoritative voice. Avoid slang. Lead with value propositions.",
    "casual": "Write like a smart friend recommending something. Contractions are fine. Be warm.",
    "urgent": "Create genuine urgency without being manipulative. Use time-sensitive language and scarcity cues.",
    "witty": "Be clever and memorable. Use wordplay where natural. Never force humor.",
    "inspirational": "Elevate the reader. Paint a vision of transformation. Use aspirational language.",
}


class PromptEngine:
    """Builds system and user prompts for the copy generation model."""

    SYSTEM_PROMPT = (
        "You are CopyGen, an expert direct-response copywriter with 15 years of "
        "experience across digital advertising, email marketing, and social media. "
        "You understand consumer psychology, AIDA frameworks, and platform-specific "
        "best practices.\n\n"
        "RULES:\n"
        "1. Return EXACTLY 3 distinct copy variations.\n"
        "2. Each variation must take a different creative angle.\n"
        "3. Every variation MUST contain a clear call-to-action (CTA).\n"
        "4. Respect platform character/format constraints precisely.\n"
        "5. Never fabricate statistics or make unverifiable claims about the product.\n"
        "6. Output ONLY valid JSON — no markdown, no commentary, no code fences.\n\n"
        "OUTPUT FORMAT (strict JSON array):\n"
        '[{"variation": 1, "copy": "..."}, {"variation": 2, "copy": "..."}, '
        '{"variation": 3, "copy": "..."}]'
    )

    @classmethod
    def build_user_prompt(
        cls,
        product_name: str,
        product_description: str,
        target_audience: str,
        tone: str,
        platform: str,
    ) -> str:
        platform_guide = PLATFORM_GUIDELINES.get(platform, "Follow general best practices.")
        tone_guide = TONE_MODIFIERS.get(tone, "")

        return (
            f"PRODUCT: {product_name}\n"
            f"DESCRIPTION: {product_description}\n"
            f"TARGET AUDIENCE: {target_audience}\n"
            f"TONE: {tone} — {tone_guide}\n"
            f"PLATFORM: {platform}\n"
            f"PLATFORM GUIDELINES: {platform_guide}\n\n"
            "Generate 3 high-converting copy variations now."
        )
