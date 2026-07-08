from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = [
        "product",
        "vendor",
        "product_name",
        "product_sku",
        "unit_price",
        "quantity",
        "line_total",
    ]

    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "order_number",
        "user",
        "status",
        "subtotal_amount",
        "tax_amount",
        "shipping_fee",
        "total_amount",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["order_number", "user__username", "user__email"]
    readonly_fields = [
        "order_number",
        "subtotal_amount",
        "tax_amount",
        "shipping_fee",
        "total_amount",
        "created_at",
        "updated_at",
        "cancelled_at",
    ]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "order",
        "product_name",
        "product_sku",
        "vendor",
        "unit_price",
        "quantity",
        "line_total",
    ]
    search_fields = ["order__order_number", "product_name", "product_sku", "vendor__username"]
