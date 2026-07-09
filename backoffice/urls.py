from django.urls import path

from .views import (
    AdminDashboardSummaryView,
    SupportOrderSearchView,
    SupportOrderStatusUpdateView,
    VendorDashboardSummaryView,
    VendorInventoryUpdateView,
    VendorProductListView,
)

urlpatterns = [
    path("admin/summary/", AdminDashboardSummaryView.as_view(), name="admin-summary"),

    path("vendor/summary/", VendorDashboardSummaryView.as_view(), name="vendor-summary"),
    path("vendor/products/", VendorProductListView.as_view(), name="vendor-products"),
    path("vendor/products/<int:pk>/inventory/", VendorInventoryUpdateView.as_view(), name="vendor-inventory-update"),

    path("support/orders/", SupportOrderSearchView.as_view(), name="support-order-search"),
    path("support/orders/<int:pk>/status/", SupportOrderStatusUpdateView.as_view(), name="support-order-status-update"),
]
