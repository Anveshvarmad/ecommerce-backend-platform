from rest_framework import serializers

from orders.models import Order
from products.models import Product


class VendorInventoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "price",
            "stock_quantity",
            "is_active",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "name",
            "sku",
            "price",
            "updated_at",
        ]

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value


class SupportOrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            Order.Status.PROCESSING,
            Order.Status.SHIPPED,
            Order.Status.DELIVERED,
            Order.Status.CANCELLED,
            Order.Status.REFUNDED,
        ]
    )
    note = serializers.CharField(required=False, allow_blank=True)

    def validate_status(self, value):
        order = self.context["order"]

        allowed_transitions = {
            Order.Status.PENDING_PAYMENT: [
                Order.Status.CANCELLED,
            ],
            Order.Status.PAYMENT_FAILED: [
                Order.Status.CANCELLED,
            ],
            Order.Status.PAID: [
                Order.Status.PROCESSING,
                Order.Status.CANCELLED,
                Order.Status.REFUNDED,
            ],
            Order.Status.PROCESSING: [
                Order.Status.SHIPPED,
                Order.Status.CANCELLED,
                Order.Status.REFUNDED,
            ],
            Order.Status.SHIPPED: [
                Order.Status.DELIVERED,
            ],
            Order.Status.DELIVERED: [
                Order.Status.REFUNDED,
            ],
            Order.Status.CANCELLED: [],
            Order.Status.REFUNDED: [],
        }

        if value not in allowed_transitions.get(order.status, []):
            raise serializers.ValidationError(
                f"Cannot move order from {order.status} to {value}."
            )

        return value
