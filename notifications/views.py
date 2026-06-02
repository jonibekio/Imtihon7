from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from notifications.models import Notification, NotificationPreference
from notifications.serializers import NotificationPreferenceSerializer, NotificationSerializer


class NotificationViewSet(ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    @action(detail=True, methods=["patch"])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at", "updated_at"])
        return Response(self.get_serializer(notification).data)


class NotificationPreferenceViewSet(ModelViewSet):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return NotificationPreference.objects.none()
        return NotificationPreference.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        preference, created = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(preference)
        return Response(serializer.data)
