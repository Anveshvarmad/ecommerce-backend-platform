import pytest

from cart.models import Cart
from orders.models import Order


@pytest.mark.django_db
def test_customer_can_checkout_active_cart(auth_client, customer, active_cart, product):
    client = auth_client(customer)

    response = client.post(
        "/api/orders/checkout/",
        {
            "shipping_address": {
                "full_name": "Test Customer",
                "line1": "123 Main Street",
                "city": "Jersey City",
                "state": "NJ",
                "postal_code": "07302",
                "country": "USA",
            },
            "notes": "Checkout test",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["status"] == "PENDING_PAYMENT"
    assert response.data["total_items"] == 2
    assert Order.objects.count() == 1

    product.refresh_from_db()
    active_cart.refresh_from_db()

    assert product.stock_quantity == 18
    assert active_cart.status == Cart.Status.CHECKED_OUT


@pytest.mark.django_db
def test_customer_can_list_own_orders(auth_client, customer, pending_order):
    client = auth_client(customer)

    response = client.get("/api/orders/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["order_number"] == pending_order.order_number


@pytest.mark.django_db
def test_customer_can_cancel_pending_order(auth_client, customer, pending_order, product):
    client = auth_client(customer)

    response = client.post(f"/api/orders/{pending_order.id}/cancel/")

    assert response.status_code == 200

    pending_order.refresh_from_db()
    product.refresh_from_db()

    assert pending_order.status == Order.Status.CANCELLED
    assert product.stock_quantity == 22
