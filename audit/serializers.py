from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "actor",
            "actor_username",
            "action",
            "method",
            "path",
            "status_code",
            "resource_type",
            "resource_id",
            "ip_address",
            "user_agent",
            "correlation_id",
            "metadata",
            "created_at",
        ]
        read_only_fields = fields
