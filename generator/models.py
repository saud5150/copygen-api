import uuid

from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator


class Tone(models.TextChoices):
    PROFESSIONAL = "professional", "Professional"
    CASUAL = "casual", "Casual"
    URGENT = "urgent", "Urgent"
    WITTY = "witty", "Witty"
    INSPIRATIONAL = "inspirational", "Inspirational"


class Platform(models.TextChoices):
    INSTAGRAM = "instagram", "Instagram"
    LINKEDIN = "linkedin", "LinkedIn"
    GOOGLE_AD = "google_ad", "Google Ad"
    EMAIL_SUBJECT = "email_subject", "Email Subject"
    FACEBOOK = "facebook", "Facebook"
    TWITTER = "twitter", "Twitter / X"


class CopyGeneration(models.Model):
    """Stores every generation request and its AI-produced variations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(
        max_length=64,
        db_index=True,
        validators=[MinLengthValidator(8), MaxLengthValidator(64)],
        help_text="Client-supplied session identifier for grouping requests.",
    )

    # Inputs
    product_name = models.CharField(max_length=200)
    product_description = models.TextField(max_length=2000)
    target_audience = models.CharField(max_length=300)
    tone = models.CharField(max_length=20, choices=Tone.choices)
    platform = models.CharField(max_length=20, choices=Platform.choices)

    # Outputs — stored as JSON list of dicts
    variations = models.JSONField(
        default=list,
        help_text='List of {"copy": str, "persuasion_score": float} objects.',
    )

    # Metadata
    model_used = models.CharField(max_length=50, default="gpt-4o")
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    latency_ms = models.PositiveIntegerField(default=0)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["session_id", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.product_name} — {self.platform} ({self.created_at:%Y-%m-%d %H:%M})"

    @property
    def total_tokens(self):
        return self.prompt_tokens + self.completion_tokens
