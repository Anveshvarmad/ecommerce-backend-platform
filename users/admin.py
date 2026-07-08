from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        "id",
        "username",
        "email",
        "role",
        "is_verified",
        "is_active",
        "is_staff",
    ]
    list_filter = [
        "role",
        "is_verified",
        "is_active",
        "is_staff",
    ]

    fieldsets = UserAdmin.fieldsets + (
        (
            "E-Commerce Role Info",
            {
                "fields": (
                    "role",
                    "phone_number",
                    "is_verified",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "E-Commerce Role Info",
            {
                "fields": (
                    "email",
                    "role",
                    "phone_number",
                    "is_verified",
                )
            },
        ),
    )
