from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAdminRole, IsAdminOrSupportRole, IsVendorRole
from .serializers import RegisterSerializer, UserProfileSerializer


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        return {"request": self.request}


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AdminOnlyView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get(self, request):
        return Response({
            "message": "Admin access granted",
            "user": request.user.username,
            "role": request.user.role,
        })


class VendorOnlyView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVendorRole]

    def get(self, request):
        return Response({
            "message": "Vendor access granted",
            "user": request.user.username,
            "role": request.user.role,
        })


class SupportOrAdminView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupportRole]

    def get(self, request):
        return Response({
            "message": "Support/Admin access granted",
            "user": request.user.username,
            "role": request.user.role,
        })
