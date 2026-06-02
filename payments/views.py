from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from payments.models import Payment
from payments.serializers import PaymentSerializer


class PaymentViewSet(ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Payment.objects.none()
        return Payment.objects.filter(user=self.request.user).select_related("order").order_by("-created_at")

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]
        serializer.save(user=self.request.user, amount=order.total_price)
