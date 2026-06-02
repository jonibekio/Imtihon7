from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cart.views import CartItemViewSet, CartViewSet

router = DefaultRouter()
router.register("cart/items", CartItemViewSet, basename="cart-item")
router.register("cart", CartViewSet, basename="cart")

urlpatterns = [
    path("", include(router.urls)),
]
