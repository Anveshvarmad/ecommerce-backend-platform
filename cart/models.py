from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator

from products.models import Product


class Cart(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CHECKED_OUT = "CHECKED_OUT", "Checked Out"
        ABANDONED = "ABANDONED", "Abandoned"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["status"]),
            models.Index(fields=["updated_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(status="ACTIVE"),
                name="unique_active_cart_per_user",
            )
        ]

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        total = Decimal("0.00")
        for item in self.items.all():
            total += item.line_total
        return total

    def __str__(self):
        return f"Cart #{self.id} - {self.user.username} - {self.status}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        default=1,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["cart", "product"]
        indexes = [
            models.Index(fields=["cart"]),
            models.Index(fields=["product"]),
            models.Index(fields=["updated_at"]),
        ]

    @property
    def line_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
