from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "status",
        "created_at",
        "updated_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "cart",
        "product",
        "quantity",
        "created_at",
        "updated_at",
    ]
    search_fields = ["product__name", "product__sku", "cart__user__username"]
    readonly_fields = ["created_at", "updated_at"]
