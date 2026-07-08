from decimal import Decimal

from rest_framework import serializers

from .models import Order, OrderItem


class CheckoutSerializer(serializers.Serializer):
    shipping_address = serializers.DictField()
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_shipping_address(self, value):
        required_fields = ["full_name", "line1", "city", "state", "postal_code", "country"]

        missing = [field for field in required_fields if not value.get(field)]
        if missing:
            raise serializers.ValidationError(
                f"Missing shipping address fields: {', '.join(missing)}"
            )

        return value


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "vendor",
            "product_name",
            "product_sku",
            "unit_price",
            "quantity",
            "line_total",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "user",
            "user_username",
            "status",
            "subtotal_amount",
            "tax_amount",
            "shipping_fee",
            "total_amount",
            "shipping_address",
            "notes",
            "total_items",
            "items",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "order_number",
            "user",
            "user_username",
            "status",
            "subtotal_amount",
            "tax_amount",
            "shipping_fee",
            "total_amount",
            "total_items",
            "items",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())
