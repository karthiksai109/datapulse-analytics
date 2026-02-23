import logging
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger("analytics")


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "healthy", "service": "datapulse-django"})


@api_view(["GET"])
@permission_classes([AllowAny])
def readiness_check(request):
    checks = {"database": False}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database readiness check failed: {e}")

    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503
    return Response(
        {"status": "ready" if all_ready else "not_ready", "checks": checks},
        status=status_code,
    )
