from django.db import connection
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET"])
def health_check(request):
    health = {
        "status": "ok",
        "database": "unknown",
        "redis": "unknown",
        "service": "ecommerce-backend-platform",
    }

    try:
        connection.ensure_connection()
        health["database"] = "connected"
    except Exception as exc:
        health["database"] = f"error: {str(exc)}"
        health["status"] = "degraded"

    try:
        cache.set("health_check", "ok", timeout=10)
        redis_value = cache.get("health_check")

        if redis_value == "ok":
            health["redis"] = "connected"
        else:
            health["redis"] = "error"
            health["status"] = "degraded"
    except Exception as exc:
        health["redis"] = f"error: {str(exc)}"
        health["status"] = "degraded"

    response_status = status.HTTP_200_OK if health["status"] == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE

    return Response(health, status=response_status)
