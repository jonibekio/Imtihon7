from rest_framework import serializers

from orders.models import Order, Status as OrderStatus
from products.models import Status as ProductStatus
from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ("is_approved",)

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating 1 dan 5 gacha bo'lishi kerak")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        product = attrs.get("product") or getattr(self.instance, "product", None)

        if product and product.status != ProductStatus.PUBLISHED:
            raise serializers.ValidationError({"product": "Bu product sotuvda emas"})

        if request and request.user.is_authenticated and product:
            has_completed_order = Order.objects.filter(
                user=request.user,
                status=OrderStatus.COMPLETED,
                items__product=product,
            ).exists()
            if not has_completed_order:
                raise serializers.ValidationError("Faqat sotib olingan product uchun review yozish mumkin")

            review = Review.objects.filter(user=request.user, product=product)
            if self.instance:
                review = review.exclude(id=self.instance.id)
            if review.exists():
                raise serializers.ValidationError("Bu product uchun review yozilgansiz")

        return attrs
