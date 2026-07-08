from django.db.models import Count, Q
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Category, Product
from .permissions import (
    IsAdminOrReadOnly,
    IsProductOwnerOrAdminOrReadOnly,
    IsVendorOrAdminForCreate,
)
from .serializers import CategorySerializer, ProductSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Category.objects.annotate(product_count=Count("products"))

        include_inactive = self.request.query_params.get("include_inactive")
        if include_inactive != "true":
            queryset = queryset.filter(is_active=True)

        q = self.request.query_params.get("q")
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )

        return queryset


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.annotate(product_count=Count("products"))
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsVendorOrAdminForCreate]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = (
            Product.objects
            .select_related("vendor", "category")
            .filter(is_active=True)
        )

        q = self.request.query_params.get("q")
        category = self.request.query_params.get("category")
        vendor = self.request.query_params.get("vendor")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        in_stock = self.request.query_params.get("in_stock")
        ordering = self.request.query_params.get("ordering")

        if q:
            queryset = queryset.filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(sku__icontains=q)
                | Q(category__name__icontains=q)
            )

        if category:
            queryset = queryset.filter(category__slug=category)

        if vendor:
            queryset = queryset.filter(vendor__username=vendor)

        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        if in_stock == "true":
            queryset = queryset.filter(stock_quantity__gt=0)

        allowed_ordering = {
            "price": "price",
            "-price": "-price",
            "created_at": "created_at",
            "-created_at": "-created_at",
            "name": "name",
            "-name": "-name",
        }

        if ordering in allowed_ordering:
            queryset = queryset.order_by(allowed_ordering[ordering])

        return queryset

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsProductOwnerOrAdminOrReadOnly,
    ]

    def get_queryset(self):
        return Product.objects.select_related("vendor", "category")

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.is_active = False
        product.save(update_fields=["is_active", "updated_at"])
        return Response({"message": "Product deactivated successfully."})
