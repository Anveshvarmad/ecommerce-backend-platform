import pytest

from orders.models import Order
from payments.models import Payment


@pytest.mark.django_db
def test_customer_can_initiate_successful_fake_payment(auth_client, customer, pending_order):
    client = auth_client(customer)

    response = client.post(
        "/api/payments/initiate/",
        {
            "order_id": pending_order.id,
            "idempotency_key": "test-payment-success",
            "force_outcome": "SUCCESS",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["status"] == "SUCCEEDED"

    pending_order.refresh_from_db()

    assert pending_order.status == Order.Status.PAID
    assert Payment.objects.count() == 1


@pytest.mark.django_db
def test_payment_idempotency_returns_existing_payment(auth_client, customer, pending_order):
    client = auth_client(customer)

    payload = {
        "order_id": pending_order.id,
        "idempotency_key": "same-key-test",
        "force_outcome": "SUCCESS",
    }

    first_response = client.post("/api/payments/initiate/", payload, format="json")

    pending_order.status = Order.Status.PENDING_PAYMENT
    pending_order.save(update_fields=["status"])

    second_response = client.post("/api/payments/initiate/", payload, format="json")

    assert first_response.status_code == 201
    assert second_response.status_code == 200
    assert first_response.data["payment_number"] == second_response.data["payment_number"]
    assert Payment.objects.count() == 1


@pytest.mark.django_db
def test_failed_payment_marks_order_payment_failed(auth_client, customer, pending_order):
    client = auth_client(customer)

    response = client.post(
        "/api/payments/initiate/",
        {
            "order_id": pending_order.id,
            "idempotency_key": "test-payment-failed",
            "force_outcome": "FAILED",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["status"] == "FAILED"

    pending_order.refresh_from_db()

    assert pending_order.status == Order.Status.PAYMENT_FAILED
