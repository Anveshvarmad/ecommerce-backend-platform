from django.db.models import Count, Q
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .cache_utils import (
    build_catalog_cache_key,
    get_cached_catalog_response,
    invalidate_catalog_cache,
    set_cached_catalog_response,
)
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


class CachedListMixin:
    cache_namespace = "catalog-list"

    def list(self, request, *args, **kwargs):
        cache_key = build_catalog_cache_key(request, self.cache_namespace)
        cached_data = get_cached_catalog_response(cache_key)

        if cached_data is not None:
            return Response(cached_data, headers={"X-Cache": "HIT"})

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)

        set_cached_catalog_response(cache_key, response.data)
        response["X-Cache"] = "MISS"
        return response


class CachedRetrieveMixin:
    cache_namespace = "catalog-detail"

    def retrieve(self, request, *args, **kwargs):
        cache_key = build_catalog_cache_key(request, self.cache_namespace)
        cached_data = get_cached_catalog_response(cache_key)

        if cached_data is not None:
            return Response(cached_data, headers={"X-Cache": "HIT"})

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response = Response(serializer.data)
        set_cached_catalog_response(cache_key, response.data)
        response["X-Cache"] = "MISS"
        return response


class CategoryListCreateView(CachedListMixin, generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    cache_namespace = "category-list"

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

    def perform_create(self, serializer):
        serializer.save()
        invalidate_catalog_cache()


class CategoryDetailView(CachedRetrieveMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.annotate(product_count=Count("products"))
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    cache_namespace = "category-detail"

    def perform_update(self, serializer):
        serializer.save()
        invalidate_catalog_cache()

    def perform_destroy(self, instance):
        instance.delete()
        invalidate_catalog_cache()


class ProductListCreateView(CachedListMixin, generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsVendorOrAdminForCreate]
    pagination_class = StandardResultsSetPagination
    cache_namespace = "product-list"

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
        invalidate_catalog_cache()


class ProductDetailView(CachedRetrieveMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsProductOwnerOrAdminOrReadOnly,
    ]
    cache_namespace = "product-detail"

    def get_queryset(self):
        return Product.objects.select_related("vendor", "category")

    def perform_update(self, serializer):
        serializer.save()
        invalidate_catalog_cache()

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.is_active = False
        product.save(update_fields=["is_active", "updated_at"])
        invalidate_catalog_cache()
        return Response({"message": "Product deactivated successfully."})
