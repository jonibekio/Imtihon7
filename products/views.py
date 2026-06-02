from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from common.permissions import IsSeller
from products.models import Product, ProductImage, Status
from products.serializers import ProductImageSerializer, ProductSerializer


class ProductViewSet(ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ("category", "seller")
    search_fields = ("title", "description")
    ordering_fields = ("price", "created_at")
    ordering = ("-created_at",)

    def get_queryset(self):
        return Product.objects.filter(status=Status.PUBLISHED).select_related(
            "category",
            "seller",
        ).prefetch_related("images", "reviews")


class SellerProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsSeller]
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ("status", "category")
    search_fields = ("title", "description")
    ordering_fields = ("price", "created_at")
    ordering = ("-created_at",)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Product.objects.none()
        return Product.objects.filter(seller=self.request.user).select_related(
            "category",
            "seller",
        ).prefetch_related("images")

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ProductImage.objects.none()
        return ProductImage.objects.filter(product__seller=self.request.user).select_related("product")

    def perform_create(self, serializer):
        serializer.save()
