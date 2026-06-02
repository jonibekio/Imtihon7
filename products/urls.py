from django.urls import include, path
from rest_framework.routers import DefaultRouter

from products.views import ProductImageViewSet, ProductViewSet, SellerProductViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("seller/products", SellerProductViewSet, basename="seller-product")
router.register("seller/product-images", ProductImageViewSet, basename="seller-product-image")

urlpatterns = [
    path("", include(router.urls)),
]
