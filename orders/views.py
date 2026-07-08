from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart, CartItem
from products.models import Product
from users.permissions import IsCustomerRole

from .models import Order, OrderItem
from .serializers import CheckoutSerializer, OrderSerializer


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerRole]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cart = (
                Cart.objects
                .select_for_update()
                .get(user=request.user, status=Cart.Status.ACTIVE)
            )
        except Cart.DoesNotExist:
            return Response(
                {"detail": "Active cart not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_items = list(
            CartItem.objects
            .select_related("product", "product__vendor")
            .filter(cart=cart)
        )

        if not cart_items:
            return Response(
                {"detail": "Cannot checkout with an empty cart."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product_ids = [item.product_id for item in cart_items]

        locked_products = {
            product.id: product
            for product in Product.objects.select_for_update().filter(id__in=product_ids)
        }

        subtotal = Decimal("0.00")

        for item in cart_items:
            product = locked_products.get(item.product_id)

            if not product:
                return Response(
                    {"detail": f"Product {item.product_id} no longer exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not product.is_active:
                return Response(
                    {"detail": f"Product {product.name} is no longer active."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if item.quantity > product.stock_quantity:
                return Response(
                    {
                        "detail": f"Only {product.stock_quantity} units available for {product.name}.",
                        "requested_quantity": item.quantity,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subtotal += product.price * item.quantity

        tax_amount = (subtotal * Decimal("0.0825")).quantize(Decimal("0.01"))
        shipping_fee = Decimal("0.00") if subtotal >= Decimal("100.00") else Decimal("9.99")
        total_amount = subtotal + tax_amount + shipping_fee

        order = Order.objects.create(
            user=request.user,
            cart=cart,
            status=Order.Status.PENDING_PAYMENT,
            subtotal_amount=subtotal,
            tax_amount=tax_amount,
            shipping_fee=shipping_fee,
            total_amount=total_amount,
            shipping_address=serializer.validated_data["shipping_address"],
            notes=serializer.validated_data.get("notes", ""),
        )

        order_items = []

        for item in cart_items:
            product = locked_products[item.product_id]
            line_total = product.price * item.quantity

            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    vendor=product.vendor,
                    product_name=product.name,
                    product_sku=product.sku,
                    unit_price=product.price,
                    quantity=item.quantity,
                    line_total=line_total,
                )
            )

            product.stock_quantity -= item.quantity
            product.save(update_fields=["stock_quantity", "updated_at"])

        OrderItem.objects.bulk_create(order_items)

        cart.status = Cart.Status.CHECKED_OUT
        cart.save(update_fields=["status", "updated_at"])

        response_serializer = OrderSerializer(
            Order.objects.prefetch_related("items").select_related("user").get(id=order.id)
        )

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = (
            Order.objects
            .select_related("user")
            .prefetch_related("items")
        )

        if user.role in ["ADMIN", "SUPPORT"]:
            return queryset

        return queryset.filter(user=user)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = (
            Order.objects
            .select_related("user")
            .prefetch_related("items")
        )

        if user.role in ["ADMIN", "SUPPORT"]:
            return queryset

        return queryset.filter(user=user)


class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        user = request.user

        queryset = (
            Order.objects
            .select_for_update()
            .prefetch_related("items")
        )

        if user.role not in ["ADMIN", "SUPPORT"]:
            queryset = queryset.filter(user=user)

        try:
            order = queryset.get(pk=pk)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if order.status not in [Order.Status.PENDING_PAYMENT]:
            return Response(
                {"detail": f"Order cannot be cancelled from status {order.status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        items = list(order.items.all())
        product_ids = [item.product_id for item in items if item.product_id]

        locked_products = {
            product.id: product
            for product in Product.objects.select_for_update().filter(id__in=product_ids)
        }

        for item in items:
            if item.product_id and item.product_id in locked_products:
                product = locked_products[item.product_id]
                product.stock_quantity += item.quantity
                product.save(update_fields=["stock_quantity", "updated_at"])

        order.status = Order.Status.CANCELLED
        order.cancelled_at = timezone.now()
        order.save(update_fields=["status", "cancelled_at", "updated_at"])

        return Response(
            {
                "message": "Order cancelled successfully.",
                "order_number": order.order_number,
            },
            status=status.HTTP_200_OK,
        )
