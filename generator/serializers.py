from rest_framework import serializers

from .models import CopyGeneration, Tone, Platform


class GenerationRequestSerializer(serializers.Serializer):
    """Validates incoming copy-generation requests."""

    product_name = serializers.CharField(
        max_length=200,
        min_length=2,
        help_text="Name of the product or service.",
    )
    product_description = serializers.CharField(
        max_length=2000,
        min_length=10,
        help_text="Detailed description of what the product does and its key benefits.",
    )
    target_audience = serializers.CharField(
        max_length=300,
        min_length=5,
        help_text="Who this copy is targeting (e.g., 'SaaS founders aged 25-40').",
    )
    tone = serializers.ChoiceField(
        choices=Tone.choices,
        help_text="Desired tone of the generated copy.",
    )
    platform = serializers.ChoiceField(
        choices=Platform.choices,
        help_text="Target distribution platform.",
    )
    session_id = serializers.CharField(
        max_length=64,
        min_length=8,
        help_text="Client session ID for request grouping and history.",
    )

    def validate_product_description(self, value: str) -> str:
        word_count = len(value.split())
        if word_count < 3:
            raise serializers.ValidationError(
                "Description must contain at least 3 words for meaningful copy generation."
            )
        return value.strip()

    def validate_product_name(self, value: str) -> str:
        return value.strip()

    def validate_target_audience(self, value: str) -> str:
        return value.strip()


class VariationSerializer(serializers.Serializer):
    copy = serializers.CharField()
    persuasion_score = serializers.FloatField()


class GenerationResponseSerializer(serializers.ModelSerializer):
    """Shapes the API response returned after a successful generation."""

    variations = VariationSerializer(many=True, read_only=True)

    class Meta:
        model = CopyGeneration
        fields = [
            "id",
            "session_id",
            "product_name",
            "platform",
            "tone",
            "variations",
            "model_used",
            "latency_ms",
            "created_at",
        ]
        read_only_fields = fields


class GenerationHistorySerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing past generations."""

    variation_count = serializers.SerializerMethodField()
    avg_score = serializers.SerializerMethodField()

    class Meta:
        model = CopyGeneration
        fields = [
            "id",
            "product_name",
            "platform",
            "tone",
            "variation_count",
            "avg_score",
            "created_at",
        ]

    def get_variation_count(self, obj: CopyGeneration) -> int:
        return len(obj.variations) if obj.variations else 0

    def get_avg_score(self, obj: CopyGeneration) -> float | None:
        if not obj.variations:
            return None
        scores = [v.get("persuasion_score", 0) for v in obj.variations]
        return round(sum(scores) / len(scores), 1) if scores else None
