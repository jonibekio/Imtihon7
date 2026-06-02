from rest_framework import serializers
from products.models import Product, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"

    def validate_product(self, product):
        request = self.context.get("request")
        if request and product.seller != request.user:
            raise serializers.ValidationError("Bu product sizga tegishli emas")
        return product

    def validate_image(self, image):
        max_size = 5 * 1024 * 1024
        if image.size > max_size:
            raise serializers.ValidationError("Rasm hajmi 5MB dan oshmasligi kerak")

        content_type = getattr(image, "content_type", "")
        if content_type and content_type not in ("image/jpeg", "image/png", "image/webp"):
            raise serializers.ValidationError("Faqat JPG, PNG yoki WEBP rasm yuklash mumkin")
        return image

    def validate(self, attrs):
        product = attrs.get("product", getattr(self.instance, "product", None))
        is_main = attrs.get("is_main", getattr(self.instance, "is_main", False))

        if product and is_main:
            query = ProductImage.objects.filter(product=product, is_main=True)
            if self.instance:
                query = query.exclude(id=self.instance.id)
            if query.exists():
                raise serializers.ValidationError({"is_main": "Bu productda asosiy rasm allaqachon bor"})

        return attrs

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    seller = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"

    def validate(self, attrs):
        price = attrs.get("price", getattr(self.instance, "price", None))
        discount_price = attrs.get("discount_price", getattr(self.instance, "discount_price", None))
        stock = attrs.get("stock", getattr(self.instance, "stock", None))

        if price is not None and price <= 0:
            raise serializers.ValidationError({"price": "Narx 0 dan katta bo'lishi kerak"})

        if discount_price is not None and discount_price <= 0:
            raise serializers.ValidationError({"discount_price": "Chegirma narxi 0 dan katta bo'lishi kerak"})

        if discount_price and price and discount_price >= price:
            raise serializers.ValidationError({
                "discount_price": "Chegirma narxi asosiy narxdan kichik bo'lishi kerak"
            })

        if stock is not None and stock < 0:
            raise serializers.ValidationError({"stock": "Stock manfiy bo'lishi mumkin emas"})

        return attrs
