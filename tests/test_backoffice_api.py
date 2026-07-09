import pytest

from orders.models import Order


@pytest.mark.django_db
def test_admin_can_view_dashboard_summary(auth_client, admin_user, pending_order):
    client = auth_client(admin_user)

    response = client.get("/api/backoffice/admin/summary/")

    assert response.status_code == 200
    assert "users" in response.data
    assert "orders" in response.data
    assert "catalog" in response.data


@pytest.mark.django_db
def test_customer_cannot_view_admin_dashboard(auth_client, customer):
    client = auth_client(customer)

    response = client.get("/api/backoffice/admin/summary/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_vendor_can_view_vendor_products(auth_client, vendor, product):
    client = auth_client(vendor)

    response = client.get("/api/backoffice/vendor/products/")

    assert response.status_code == 200
    assert response.data[0]["sku"] == product.sku


@pytest.mark.django_db
def test_support_can_update_paid_order_to_processing(auth_client, support, pending_order):
    pending_order.status = Order.Status.PAID
    pending_order.save(update_fields=["status"])

    client = auth_client(support)

    response = client.patch(
        f"/api/backoffice/support/orders/{pending_order.id}/status/",
        {
            "status": "PROCESSING",
            "note": "Moving order into processing.",
        },
        format="json",
    )

    assert response.status_code == 200

    pending_order.refresh_from_db()

    assert pending_order.status == Order.Status.PROCESSING
