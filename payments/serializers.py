import uuid

from rest_framework import serializers

from orders.models import Order
from .models import Payment, PaymentEvent


class PaymentInitiateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    idempotency_key = serializers.CharField(required=False, allow_blank=True)
    force_outcome = serializers.ChoiceField(
        choices=["SUCCESS", "FAILED", "TIMEOUT"],
        required=False,
    )

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        try:
            order = Order.objects.get(id=attrs["order_id"])
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")

        if user.role not in ["ADMIN", "SUPPORT"] and order.user_id != user.id:
            raise serializers.ValidationError("You do not have access to this order.")

        if order.status == Order.Status.PAID:
            raise serializers.ValidationError("Order is already paid.")

        if order.status not in [Order.Status.PENDING_PAYMENT, Order.Status.PAYMENT_FAILED]:
            raise serializers.ValidationError(f"Cannot pay order from status {order.status}.")

        attrs["order"] = order

        if not attrs.get("idempotency_key"):
            attrs["idempotency_key"] = str(uuid.uuid4())

        return attrs


class PaymentEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentEvent
        fields = [
            "id",
            "event_type",
            "payload",
            "created_at",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    events = PaymentEventSerializer(many=True, read_only=True)
    order_number = serializers.CharField(source="order.order_number", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "payment_number",
            "order",
            "order_number",
            "user",
            "username",
            "provider",
            "status",
            "amount",
            "currency",
            "idempotency_key",
            "provider_reference",
            "failure_reason",
            "request_payload",
            "response_payload",
            "events",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "payment_number",
            "order",
            "order_number",
            "user",
            "username",
            "provider",
            "status",
            "amount",
            "currency",
            "provider_reference",
            "failure_reason",
            "request_payload",
            "response_payload",
            "events",
            "created_at",
            "updated_at",
        ]


class FakeWebhookSerializer(serializers.Serializer):
    payment_number = serializers.CharField()
    status = serializers.ChoiceField(choices=["SUCCEEDED", "FAILED", "TIMEOUT"])
    event_type = serializers.CharField(required=False, allow_blank=True)
    message = serializers.CharField(required=False, allow_blank=True)
