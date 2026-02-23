from django.urls import path
from .health_views import health_check, readiness_check

urlpatterns = [
    path("live/", health_check, name="health-check"),
    path("ready/", readiness_check, name="readiness-check"),
]
