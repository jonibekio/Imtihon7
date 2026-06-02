from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from cart.models import CartItem
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer
from products.models import Product, Status as ProductStatus


class OrderViewSet(ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product__images").order_by("-created_at")

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        cart_items = CartItem.objects.filter(cart__user=request.user).select_related("product")

        if not cart_items.exists():
            return Response({"detail": "Cart bo'sh"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            cart_items = CartItem.objects.filter(cart__user=request.user).select_related("product").select_for_update()
            products = Product.objects.select_for_update().filter(id__in=[item.product_id for item in cart_items])
            product_map = {product.id: product for product in products}

            for item in cart_items:
                product = product_map[item.product_id]
                if product.status != ProductStatus.PUBLISHED:
                    return Response(
                        {"detail": f"{product.title} sotuvda emas"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if item.quantity > product.stock:
                    return Response(
                        {"detail": f"{product.title} stock yetarli emas"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            total_price = sum(
                (product_map[item.product_id].discount_price or product_map[item.product_id].price) * item.quantity
                for item in cart_items
            )
            order = Order.objects.create(user=request.user, total_price=total_price)

            for item in cart_items:
                product = product_map[item.product_id]
                price = product.discount_price or product.price
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=price,
                )
                product.stock -= item.quantity
                product.save(update_fields=["stock", "updated_at"])

            cart_items.delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
