from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "is_active",
            "product_count",
            "created_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "product_count"]


class ProductSerializer(serializers.ModelSerializer):
    vendor_username = serializers.CharField(source="vendor.username", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "vendor",
            "vendor_username",
            "category",
            "category_name",
            "name",
            "slug",
            "sku",
            "description",
            "price",
            "stock_quantity",
            "is_active",
            "image_url",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "vendor",
            "vendor_username",
            "category_name",
            "slug",
            "created_at",
            "updated_at",
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value
