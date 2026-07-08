from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsCustomerRole

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


def get_active_cart(user):
    cart, _ = Cart.objects.prefetch_related("items__product").get_or_create(
        user=user,
        status=Cart.Status.ACTIVE,
    )
    return cart


class CartDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerRole]

    def get(self, request):
        cart = get_active_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AddCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerRole]

    def post(self, request):
        cart = get_active_cart(request.user)
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        existing_item = CartItem.objects.filter(cart=cart, product=product).first()

        if existing_item:
            new_quantity = existing_item.quantity + quantity

            if new_quantity > product.stock_quantity:
                return Response(
                    {
                        "detail": f"Only {product.stock_quantity} units available in stock.",
                        "current_cart_quantity": existing_item.quantity,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            existing_item.quantity = new_quantity
            existing_item.save(update_fields=["quantity", "updated_at"])
            response_serializer = CartItemSerializer(existing_item)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        item = serializer.save(cart=cart)
        response_serializer = CartItemSerializer(item)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class UpdateCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerRole]

    def patch(self, request, item_id):
        cart = get_active_cart(request.user)

        try:
            item = CartItem.objects.select_related("product").get(
                id=item_id,
                cart=cart,
            )
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CartItemSerializer(
            item,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(CartItemSerializer(item).data)


class RemoveCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerRole]

    def delete(self, request, item_id):
        cart = get_active_cart(request.user)

        deleted_count, _ = CartItem.objects.filter(
            id=item_id,
            cart=cart,
        ).delete()

        if deleted_count == 0:
            return Response(
                {"detail": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"message": "Item removed from cart."},
            status=status.HTTP_200_OK,
        )


class ClearCartView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerRole]

    def delete(self, request):
        cart = get_active_cart(request.user)
        deleted_count, _ = cart.items.all().delete()

        return Response(
            {
                "message": "Cart cleared successfully.",
                "items_removed": deleted_count,
            },
            status=status.HTTP_200_OK,
        )
