import pytest

from cart.models import CartItem


@pytest.mark.django_db
def test_customer_can_view_empty_cart(auth_client, customer):
    client = auth_client(customer)

    response = client.get("/api/cart/")

    assert response.status_code == 200
    assert response.data["status"] == "ACTIVE"
    assert response.data["total_items"] == 0
    assert response.data["subtotal"] == "0.00"


@pytest.mark.django_db
def test_customer_can_add_product_to_cart(auth_client, customer, product):
    client = auth_client(customer)

    response = client.post(
        "/api/cart/items/",
        {
            "product_id": product.id,
            "quantity": 2,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["quantity"] == 2
    assert CartItem.objects.count() == 1


@pytest.mark.django_db
def test_customer_cannot_add_more_than_stock(auth_client, customer, product):
    client = auth_client(customer)

    response = client.post(
        "/api/cart/items/",
        {
            "product_id": product.id,
            "quantity": product.stock_quantity + 1,
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_vendor_cannot_access_customer_cart(auth_client, vendor):
    client = auth_client(vendor)

    response = client.get("/api/cart/")

    assert response.status_code == 403
