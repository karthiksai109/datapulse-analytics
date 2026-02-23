from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="DataPulse Analytics API",
        default_version="v1",
        description="Real-time data analytics and AI-powered insights platform",
        terms_of_service="https://datapulse.example.com/terms/",
        contact=openapi.Contact(email="karthik@datapulse.dev"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def root_view(request):
    return JsonResponse({
        "service": "DataPulse Django API",
        "version": "1.0.0",
        "endpoints": {
            "admin": "/admin/",
            "api": "/api/v1/",
            "swagger": "/swagger/",
            "health": "/api/v1/health/live/",
        }
    })


urlpatterns = [
    path("", root_view, name="root"),
    path("admin/", admin.site.urls),
    path("api/v1/analytics/", include("analytics.urls")),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/health/", include("analytics.health_urls")),
    # Swagger docs
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
]
