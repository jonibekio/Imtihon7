from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from addresses.models import UserAddress
from addresses.serializers import UserAddressSerializer


class UserAddressViewSet(ModelViewSet):
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return UserAddress.objects.none()
        return UserAddress.objects.filter(user=self.request.user).order_by("-is_default", "-created_at")

    def perform_create(self, serializer):
        if serializer.validated_data.get("is_default"):
            UserAddress.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.validated_data.get("is_default"):
            UserAddress.objects.filter(user=self.request.user, is_default=True).exclude(id=self.get_object().id).update(is_default=False)
        serializer.save()
