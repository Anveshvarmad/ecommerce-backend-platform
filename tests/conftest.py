import pytest
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from products.models import Category, Product
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem


@pytest.fixture(autouse=True)
def celery_eager(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_model():
    return get_user_model()


@pytest.fixture
def customer(user_model):
    user = user_model.objects.create_user(
        username="test_customer",
        email="test_customer@example.com",
        password="Password123!",
        role="CUSTOMER",
    )
    return user


@pytest.fixture
def vendor(user_model):
    user = user_model.objects.create_user(
        username="test_vendor",
        email="test_vendor@example.com",
        password="Password123!",
        role="VENDOR",
    )
    return user


@pytest.fixture
def support(user_model):
    user = user_model.objects.create_user(
        username="test_support",
        email="test_support@example.com",
        password="Password123!",
        role="SUPPORT",
    )
    return user


@pytest.fixture
def admin_user(user_model):
    user = user_model.objects.create_user(
        username="test_admin",
        email="test_admin@example.com",
        password="Password123!",
        role="ADMIN",
        is_staff=True,
        is_superuser=True,
    )
    return user


@pytest.fixture
def auth_client():
    def _make(user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    return _make


@pytest.fixture
def category():
    return Category.objects.create(
        name="Electronics",
        description="Electronic devices",
        is_active=True,
    )


@pytest.fixture
def product(vendor, category):
    return Product.objects.create(
        vendor=vendor,
        category=category,
        name="Wireless Headphones",
        sku="TEST-HEADPHONE-001",
        description="Noise cancelling wireless headphones.",
        price=Decimal("149.99"),
        stock_quantity=20,
        is_active=True,
        image_url="https://example.com/test-headphones.jpg",
        metadata={"brand": "TestBrand"},
    )


@pytest.fixture
def active_cart(customer, product):
    cart = Cart.objects.create(user=customer, status=Cart.Status.ACTIVE)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    return cart


@pytest.fixture
def pending_order(customer, vendor, product):
    subtotal = product.price * 2
    tax = (subtotal * Decimal("0.0825")).quantize(Decimal("0.01"))
    shipping = Decimal("0.00")
    total = subtotal + tax + shipping

    cart = Cart.objects.create(user=customer, status=Cart.Status.CHECKED_OUT)

    order = Order.objects.create(
        user=customer,
        cart=cart,
        status=Order.Status.PENDING_PAYMENT,
        subtotal_amount=subtotal,
        tax_amount=tax,
        shipping_fee=shipping,
        total_amount=total,
        shipping_address={
            "full_name": "Test Customer",
            "line1": "123 Main Street",
            "city": "Jersey City",
            "state": "NJ",
            "postal_code": "07302",
            "country": "USA",
        },
        notes="Test pending order",
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        vendor=vendor,
        product_name=product.name,
        product_sku=product.sku,
        unit_price=product.price,
        quantity=2,
        line_total=subtotal,
    )

    return order
