import pytest

from audit.models import AuditLog


@pytest.mark.django_db
def test_write_request_creates_audit_log(auth_client, admin_user):
    client = auth_client(admin_user)

    response = client.post(
        "/api/catalog/categories/",
        {
            "name": "Audit Test Category",
            "description": "Created during audit test.",
        },
        format="json",
        HTTP_X_REQUEST_ID="audit-test-request",
    )

    assert response.status_code == 201
    assert AuditLog.objects.filter(correlation_id="audit-test-request").exists()


@pytest.mark.django_db
def test_admin_can_view_audit_logs(auth_client, admin_user):
    AuditLog.objects.create(
        actor=admin_user,
        action=AuditLog.Action.CREATE,
        method="POST",
        path="/api/test/",
        status_code=201,
        resource_type="test",
        resource_id="1",
        correlation_id="manual-test-log",
    )

    client = auth_client(admin_user)

    response = client.get("/api/audit/logs/")

    assert response.status_code == 200
    assert len(response.data) >= 1


@pytest.mark.django_db
def test_customer_cannot_view_audit_logs(auth_client, customer):
    client = auth_client(customer)

    response = client.get("/api/audit/logs/")

    assert response.status_code == 403
