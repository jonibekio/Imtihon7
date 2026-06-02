from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from profiles.models import Profile
from profiles.serializers import ProfileSerializer


class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Profile.objects.none()
        return Profile.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
