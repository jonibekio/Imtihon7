from rest_framework import serializers

from orders.models import Status as OrderStatus
from payments.models import Payment, PaymentStatus


class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("status", "paid_at", "transaction_id", "provider")

    def validate_order(self, order):
        request = self.context.get("request")
        if request and order.user != request.user:
            raise serializers.ValidationError("Bu order sizga tegishli emas")
        return order

    def validate(self, attrs):
        order = attrs.get("order", getattr(self.instance, "order", None))
        if not order:
            return attrs

        if order.status in (OrderStatus.CANCELLED, OrderStatus.COMPLETED):
            raise serializers.ValidationError({"order": "Yakunlangan yoki bekor qilingan order uchun payment yaratib bo'lmaydi"})

        existing = Payment.objects.filter(
            order=order,
            status__in=(PaymentStatus.PENDING, PaymentStatus.PROCESSING, PaymentStatus.PAID),
        )
        if self.instance:
            existing = existing.exclude(id=self.instance.id)
        if existing.exists():
            raise serializers.ValidationError({"order": "Bu order uchun aktiv payment mavjud"})

        return attrs
