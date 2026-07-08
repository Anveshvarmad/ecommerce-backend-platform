from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AdminOnlyView,
    MeView,
    RegisterView,
    SupportOrAdminView,
    VendorOnlyView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),

    path("admin-only/", AdminOnlyView.as_view(), name="admin-only"),
    path("vendor-only/", VendorOnlyView.as_view(), name="vendor-only"),
    path("support-or-admin/", SupportOrAdminView.as_view(), name="support-or-admin"),
]
