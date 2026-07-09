from django.urls import path

from .views import (
    FakeWebhookView,
    InitiatePaymentView,
    PaymentDetailView,
    PaymentListView,
)

urlpatterns = [
    path("initiate/", InitiatePaymentView.as_view(), name="payment-initiate"),
    path("", PaymentListView.as_view(), name="payment-list"),
    path("<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
    path("webhooks/fake/", FakeWebhookView.as_view(), name="fake-payment-webhook"),
]
