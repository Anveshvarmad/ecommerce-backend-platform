import pytest


@pytest.mark.django_db
def test_customer_can_register_and_login(api_client):
    register_response = api_client.post(
        "/api/auth/register/",
        {
            "username": "new_customer",
            "email": "new_customer@example.com",
            "password": "Password123!",
            "first_name": "New",
            "last_name": "Customer",
            "role": "CUSTOMER",
        },
        format="json",
    )

    assert register_response.status_code == 201
    assert register_response.data["username"] == "new_customer"
    assert register_response.data["role"] == "CUSTOMER"

    login_response = api_client.post(
        "/api/auth/login/",
        {
            "username": "new_customer",
            "password": "Password123!",
        },
        format="json",
    )

    assert login_response.status_code == 200
    assert "access" in login_response.data
    assert "refresh" in login_response.data


@pytest.mark.django_db
def test_authenticated_user_can_view_profile(auth_client, customer):
    client = auth_client(customer)

    response = client.get("/api/auth/me/")

    assert response.status_code == 200
    assert response.data["username"] == customer.username
    assert response.data["role"] == "CUSTOMER"


@pytest.mark.django_db
def test_customer_cannot_access_admin_only_endpoint(auth_client, customer):
    client = auth_client(customer)

    response = client.get("/api/auth/admin-only/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_can_access_admin_only_endpoint(auth_client, admin_user):
    client = auth_client(admin_user)

    response = client.get("/api/auth/admin-only/")

    assert response.status_code == 200
    assert response.data["message"] == "Admin access granted"
