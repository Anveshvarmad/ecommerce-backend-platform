import pytest

from products.models import Product


@pytest.mark.django_db
def test_public_user_can_list_products(api_client, product):
    response = api_client.get("/api/catalog/products/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["sku"] == product.sku


@pytest.mark.django_db
def test_vendor_can_create_product(auth_client, vendor, category):
    client = auth_client(vendor)

    response = client.post(
        "/api/catalog/products/",
        {
            "category": category.id,
            "name": "USB-C Charger",
            "sku": "TEST-CHARGER-001",
            "description": "Fast charger",
            "price": "39.99",
            "stock_quantity": 100,
            "image_url": "https://example.com/charger.jpg",
            "metadata": {"brand": "VoltMax"},
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["vendor"] == vendor.id
    assert Product.objects.filter(sku="TEST-CHARGER-001").exists()


@pytest.mark.django_db
def test_customer_cannot_create_product(auth_client, customer, category):
    client = auth_client(customer)

    response = client.post(
        "/api/catalog/products/",
        {
            "category": category.id,
            "name": "Invalid Product",
            "sku": "INVALID-001",
            "description": "Should not be created",
            "price": "10.00",
            "stock_quantity": 10,
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_product_search_filter_works(api_client, product):
    response = api_client.get("/api/catalog/products/?q=wireless")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == product.name
