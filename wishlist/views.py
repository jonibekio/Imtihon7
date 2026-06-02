from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from wishlist.models import Wishlist, WishlistItem
from wishlist.serializers import WishlistItemSerializer, WishlistSerializer


class WishlistViewSet(ReadOnlyModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Wishlist.objects.none()
        return Wishlist.objects.filter(user=self.request.user).prefetch_related("items__product__images")

    def list(self, request, *args, **kwargs):
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(wishlist)
        return Response(serializer.data)


class WishlistItemViewSet(ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return WishlistItem.objects.none()
        return WishlistItem.objects.filter(wishlist__user=self.request.user).select_related("wishlist", "product").prefetch_related("product__images")

    def create(self, request, *args, **kwargs):
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product"]

        item, created = WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            product=product,
        )

        serializer = self.get_serializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
