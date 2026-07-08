from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=User.Role.choices,
        required=False,
        default=User.Role.CUSTOMER,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
            "phone_number",
        ]

    def validate_role(self, value):
        request = self.context.get("request")

        if value in [User.Role.ADMIN, User.Role.SUPPORT]:
            if not request or not request.user.is_authenticated or request.user.role != User.Role.ADMIN:
                raise serializers.ValidationError("Only admins can create admin or support users.")

        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone_number",
            "is_verified",
            "is_active",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "role",
            "is_verified",
            "is_active",
            "date_joined",
        ]
