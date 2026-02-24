"""Custom throttle class for daily generation limits.

Uses IP-based identification for anonymous users.
The rate is configured via REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["generation_free"].
"""

from rest_framework.throttling import SimpleRateThrottle


class DailyGenerationThrottle(SimpleRateThrottle):
    scope = "generation_free"

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}
