from rest_framework import serializers

from products.models import Product
from .models import Cart, CartItem


class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "price",
            "stock_quantity",
            "image_url",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source="product",
        write_only=True,
        required=False,
    )
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_id",
            "quantity",
            "line_total",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "product",
            "line_total",
            "created_at",
            "updated_at",
        ]

    def get_line_total(self, obj):
        return str(obj.line_total)

    def validate(self, attrs):
        product = attrs.get("product") or getattr(self.instance, "product", None)
        quantity = attrs.get("quantity") or getattr(self.instance, "quantity", 1)

        if not product:
            raise serializers.ValidationError("Product is required.")

        if not product.is_active:
            raise serializers.ValidationError("Product is not active.")

        if quantity < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")

        if quantity > product.stock_quantity:
            raise serializers.ValidationError(
                f"Only {product.stock_quantity} units available in stock."
            )

        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "status",
            "items",
            "total_items",
            "subtotal",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "status",
            "items",
            "total_items",
            "subtotal",
            "created_at",
            "updated_at",
        ]

    def get_total_items(self, obj):
        return obj.total_items

    def get_subtotal(self, obj):
        return str(obj.subtotal)
