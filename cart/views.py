from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from cart.models import Cart, CartItem
from cart.serializers import CartItemSerializer, CartSerializer


class CartViewSet(ReadOnlyModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user).prefetch_related("items__product__images")

    def list(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return CartItem.objects.none()
        return CartItem.objects.filter(cart__user=self.request.user).select_related("product", "cart").prefetch_related("product__images")

    def perform_create(self, serializer):
        with transaction.atomic():
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            product = serializer.validated_data["product"]
            quantity = serializer.validated_data.get("quantity", 1)
            item = CartItem.objects.select_for_update().filter(cart=cart, product=product).first()

            if item:
                if item.quantity + quantity > product.stock:
                    raise ValidationError({"quantity": "Product stock yetarli emas"})

                item.quantity += quantity
                item.save(update_fields=["quantity", "updated_at"])
                serializer.instance = item
            else:
                serializer.save(cart=cart)
