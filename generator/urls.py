from django.urls import path

from . import views

app_name = "generator"

urlpatterns = [
    path("generate/", views.GenerateCopyView.as_view(), name="generate"),
    path("history/", views.GenerationHistoryView.as_view(), name="history"),
    path("history/<uuid:pk>/", views.GenerationDetailView.as_view(), name="detail"),
    path("health/", views.HealthCheckView.as_view(), name="health"),
]
