from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "name"], name="cat_active_name_idx"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    image_url = models.URLField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["vendor"]),
            models.Index(fields=["category"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["price"]),
            models.Index(fields=["is_active", "category", "price"], name="prod_active_cat_price_idx"),
            models.Index(fields=["is_active", "stock_quantity"], name="prod_active_stock_idx"),
            models.Index(fields=["is_active", "created_at"], name="prod_active_created_idx"),
            models.Index(fields=["vendor", "is_active"], name="prod_vendor_active_idx"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = f"{base_slug}-{self.sku.lower()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.sku}"
