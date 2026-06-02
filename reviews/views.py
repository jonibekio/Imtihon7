from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from reviews.models import Review
from reviews.serializers import ReviewSerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Review.objects.none()
        return Review.objects.filter(user=self.request.user).select_related("user", "product").order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
