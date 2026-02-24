from django.contrib import admin

from .models import CopyGeneration


@admin.register(CopyGeneration)
class CopyGenerationAdmin(admin.ModelAdmin):
    list_display = [
        "product_name",
        "platform",
        "tone",
        "session_id",
        "model_used",
        "latency_ms",
        "created_at",
    ]
    list_filter = ["platform", "tone", "model_used", "created_at"]
    search_fields = ["product_name", "session_id"]
    readonly_fields = [
        "id",
        "variations",
        "prompt_tokens",
        "completion_tokens",
        "latency_ms",
        "ip_address",
        "created_at",
    ]
    date_hierarchy = "created_at"
