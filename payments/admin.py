from django.contrib import admin

from .models import Payment, PaymentEvent


class PaymentEventInline(admin.TabularInline):
    model = PaymentEvent
    extra = 0
    readonly_fields = ["event_type", "payload", "created_at"]
    can_delete = False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "payment_number",
        "order",
        "user",
        "provider",
        "status",
        "amount",
        "currency",
        "created_at",
    ]
    list_filter = ["provider", "status", "created_at"]
    search_fields = [
        "payment_number",
        "provider_reference",
        "idempotency_key",
        "order__order_number",
        "user__username",
        "user__email",
    ]
    readonly_fields = [
        "payment_number",
        "provider_reference",
        "request_payload",
        "response_payload",
        "failure_reason",
        "created_at",
        "updated_at",
    ]
    inlines = [PaymentEventInline]


@admin.register(PaymentEvent)
class PaymentEventAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "payment",
        "event_type",
        "created_at",
    ]
    list_filter = ["event_type", "created_at"]
    search_fields = ["payment__payment_number", "event_type"]
    readonly_fields = ["payment", "event_type", "payload", "created_at"]
