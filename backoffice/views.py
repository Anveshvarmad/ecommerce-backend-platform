from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer
from payments.models import Payment
from products.models import Product
from products.serializers import ProductSerializer
from users.permissions import IsAdminOrSupportRole, IsAdminRole, IsVendorRole

from .serializers import (
    SupportOrderStatusUpdateSerializer,
    VendorInventoryUpdateSerializer,
)


User = get_user_model()


def money(value):
    return str(value or Decimal("0.00"))


class AdminDashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get(self, request):
        paid_statuses = [
            Order.Status.PAID,
            Order.Status.PROCESSING,
            Order.Status.SHIPPED,
            Order.Status.DELIVERED,
        ]

        revenue = (
            Order.objects
            .filter(status__in=paid_statuses)
            .aggregate(total=Sum("total_amount"))
            .get("total")
        )

        order_status_counts = dict(
            Order.objects
            .values("status")
            .annotate(count=Count("id"))
            .values_list("status", "count")
        )

        payment_status_counts = dict(
            Payment.objects
            .values("status")
            .annotate(count=Count("id"))
            .values_list("status", "count")
        )

        data = {
            "users": {
                "total": User.objects.count(),
                "customers": User.objects.filter(role="CUSTOMER").count(),
                "vendors": User.objects.filter(role="VENDOR").count(),
                "support": User.objects.filter(role="SUPPORT").count(),
                "admins": User.objects.filter(role="ADMIN").count(),
            },
            "catalog": {
                "products": Product.objects.count(),
                "active_products": Product.objects.filter(is_active=True).count(),
                "low_stock_products": Product.objects.filter(is_active=True, stock_quantity__lte=10).count(),
            },
            "orders": {
                "total": Order.objects.count(),
                "by_status": order_status_counts,
                "gross_revenue": money(revenue),
            },
            "payments": {
                "total": Payment.objects.count(),
                "by_status": payment_status_counts,
            },
            "generated_at": timezone.now(),
        }

        return Response(data)


class VendorDashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVendorRole]

    def get(self, request):
        vendor = request.user

        sold_items = OrderItem.objects.filter(vendor=vendor)

        paid_sold_items = sold_items.filter(
            order__status__in=[
                Order.Status.PAID,
                Order.Status.PROCESSING,
                Order.Status.SHIPPED,
                Order.Status.DELIVERED,
            ]
        )

        revenue = paid_sold_items.aggregate(total=Sum("line_total")).get("total")

        data = {
            "vendor": {
                "id": vendor.id,
                "username": vendor.username,
                "email": vendor.email,
            },
            "products": {
                "total": Product.objects.filter(vendor=vendor).count(),
                "active": Product.objects.filter(vendor=vendor, is_active=True).count(),
                "low_stock": Product.objects.filter(
                    vendor=vendor,
                    is_active=True,
                    stock_quantity__lte=10,
                ).count(),
            },
            "sales": {
                "sold_line_items": sold_items.count(),
                "paid_line_items": paid_sold_items.count(),
                "units_sold": paid_sold_items.aggregate(total=Sum("quantity")).get("total") or 0,
                "revenue": money(revenue),
            },
            "generated_at": timezone.now(),
        }

        return Response(data)


class VendorProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendorRole]

    def get_queryset(self):
        queryset = Product.objects.select_related("vendor", "category").filter(
            vendor=self.request.user
        )

        q = self.request.query_params.get("q")
        low_stock = self.request.query_params.get("low_stock")
        is_active = self.request.query_params.get("is_active")

        if q:
            queryset = queryset.filter(
                Q(name__icontains=q)
                | Q(sku__icontains=q)
                | Q(description__icontains=q)
            )

        if low_stock == "true":
            queryset = queryset.filter(stock_quantity__lte=10)

        if is_active in ["true", "false"]:
            queryset = queryset.filter(is_active=(is_active == "true"))

        return queryset.order_by("-updated_at")


class VendorInventoryUpdateView(generics.UpdateAPIView):
    serializer_class = VendorInventoryUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendorRole]
    http_method_names = ["patch"]

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user)


class SupportOrderSearchView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupportRole]

    def get_queryset(self):
        queryset = (
            Order.objects
            .select_related("user")
            .prefetch_related("items")
            .all()
        )

        q = self.request.query_params.get("q")
        status_filter = self.request.query_params.get("status")
        customer = self.request.query_params.get("customer")

        if q:
            queryset = queryset.filter(
                Q(order_number__icontains=q)
                | Q(user__username__icontains=q)
                | Q(user__email__icontains=q)
                | Q(items__product_name__icontains=q)
                | Q(items__product_sku__icontains=q)
            ).distinct()

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if customer:
            queryset = queryset.filter(
                Q(user__username__icontains=customer)
                | Q(user__email__icontains=customer)
            )

        return queryset.order_by("-created_at")


class SupportOrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupportRole]

    def patch(self, request, pk):
        try:
            order = Order.objects.select_related("user").get(pk=pk)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SupportOrderStatusUpdateSerializer(
            data=request.data,
            context={"order": order},
        )
        serializer.is_valid(raise_exception=True)

        old_status = order.status
        new_status = serializer.validated_data["status"]
        note = serializer.validated_data.get("note", "")

        order.status = new_status

        if note:
            existing_notes = order.notes or ""
            order.notes = f"{existing_notes}\n[Support Update] {note}".strip()
            order.save(update_fields=["status", "notes", "updated_at"])
        else:
            order.save(update_fields=["status", "updated_at"])

        return Response(
            {
                "message": "Order status updated successfully.",
                "order_id": order.id,
                "order_number": order.order_number,
                "old_status": old_status,
                "new_status": order.status,
            }
        )
