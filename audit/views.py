from rest_framework import generics, permissions

from users.permissions import IsAdminRole

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        queryset = AuditLog.objects.select_related("actor").all()

        action = self.request.query_params.get("action")
        resource_type = self.request.query_params.get("resource_type")
        status_code = self.request.query_params.get("status_code")
        actor = self.request.query_params.get("actor")

        if action:
            queryset = queryset.filter(action=action)

        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)

        if status_code:
            queryset = queryset.filter(status_code=status_code)

        if actor:
            queryset = queryset.filter(actor__username__icontains=actor)

        return queryset.order_by("-created_at")
