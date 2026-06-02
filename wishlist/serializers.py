from rest_framework import serializers

from products.models import Status
from products.serializers import ProductSerializer
from wishlist.models import Wishlist, WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source="product", read_only=True)

    class Meta:
        model = WishlistItem
        fields = ("id", "wishlist", "product", "product_detail", "created_at")
        read_only_fields = ("wishlist",)

    def validate_product(self, product):
        if product.status != Status.PUBLISHED:
            raise serializers.ValidationError("Faqat sotuvdagi productni wishlistga qo'shish mumkin")
        return product


class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ("id", "user", "items", "created_at")
        read_only_fields = ("user",)
