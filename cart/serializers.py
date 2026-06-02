from rest_framework import serializers
from cart.models import Cart, CartItem
from products.models import Status
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source="product", read_only=True)

    class Meta:
        model = CartItem
        fields = ("id", "cart", "product", "product_detail", "quantity", "created_at")
        read_only_fields = ("cart",)

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity 1 dan kam bo'lmasligi kerak")
        return value

    def validate(self, attrs):
        product = attrs.get("product", getattr(self.instance, "product", None))
        quantity = attrs.get("quantity", getattr(self.instance, "quantity", 1))

        if self.instance and "product" in attrs and attrs["product"] != self.instance.product:
            raise serializers.ValidationError({"product": "Cart item productini o'zgartirib bo'lmaydi"})

        if product and product.status != Status.PUBLISHED:
            raise serializers.ValidationError({"product": "Bu product sotuvda emas"})

        if product and product.stock <= 0:
            raise serializers.ValidationError({"product": "Product stockda mavjud emas"})

        if product and quantity > product.stock:
            raise serializers.ValidationError({"quantity": "Product stock yetarli emas"})

        return attrs

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "user", "items", "created_at")
        read_only_fields = ("user",)
