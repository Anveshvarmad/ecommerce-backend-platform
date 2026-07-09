from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "action",
        "actor",
        "method",
        "path",
        "status_code",
        "resource_type",
        "resource_id",
        "ip_address",
        "created_at",
    ]
    list_filter = [
        "action",
        "method",
        "status_code",
        "resource_type",
        "created_at",
    ]
    search_fields = [
        "actor__username",
        "actor__email",
        "path",
        "resource_type",
        "resource_id",
        "correlation_id",
        "ip_address",
    ]
    readonly_fields = [
        "actor",
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

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
