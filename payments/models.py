import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models

from orders.models import Order


class Payment(models.Model):
    class Provider(models.TextChoices):
        FAKE = "FAKE", "Fake"
        STRIPE = "STRIPE", "Stripe"

    class Status(models.TextChoices):
        INITIATED = "INITIATED", "Initiated"
        PROCESSING = "PROCESSING", "Processing"
        SUCCEEDED = "SUCCEEDED", "Succeeded"
        FAILED = "FAILED", "Failed"
        TIMEOUT = "TIMEOUT", "Timeout"
        REFUNDED = "REFUNDED", "Refunded"

    payment_number = models.CharField(max_length=40, unique=True, db_index=True, editable=False)

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
        default=Provider.FAKE,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INITIATED,
        db_index=True,
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")

    idempotency_key = models.CharField(max_length=160, unique=True, db_index=True)
    provider_reference = models.CharField(max_length=160, blank=True, db_index=True)
    failure_reason = models.TextField(blank=True)

    request_payload = models.JSONField(default=dict, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["user"]),
            models.Index(fields=["status"]),
            models.Index(fields=["provider"]),
            models.Index(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.payment_number:
            self.payment_number = f"PAY-{uuid.uuid4().hex[:16].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_number} - {self.status} - {self.amount} {self.currency}"


class PaymentEvent(models.Model):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="events",
    )
    event_type = models.CharField(max_length=80, db_index=True)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["payment"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.payment.payment_number}"
