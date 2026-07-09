from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        CHECKOUT = "CHECKOUT", "Checkout"
        PAYMENT = "PAYMENT", "Payment"
        STATUS_CHANGE = "STATUS_CHANGE", "Status Change"
        AUTH = "AUTH", "Auth"
        OTHER = "OTHER", "Other"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(
        max_length=40,
        choices=Action.choices,
        default=Action.OTHER,
        db_index=True,
    )
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500, db_index=True)
    status_code = models.PositiveIntegerField(db_index=True)

    resource_type = models.CharField(max_length=120, blank=True, db_index=True)
    resource_id = models.CharField(max_length=120, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    correlation_id = models.CharField(max_length=80, blank=True, db_index=True)

    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["actor"]),
            models.Index(fields=["action"]),
            models.Index(fields=["status_code"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["resource_type", "resource_id"]),
        ]

    def __str__(self):
        actor_name = self.actor.username if self.actor else "anonymous"
        return f"{self.action} by {actor_name} - {self.method} {self.path}"
