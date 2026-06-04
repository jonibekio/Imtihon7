from django.urls import include, path
from rest_framework.routers import DefaultRouter

from wishlist.views import WishlistItemViewSet, WishlistViewSet

router = DefaultRouter()
router.register("items", WishlistItemViewSet, basename="wishlist-item")
router.register("", WishlistViewSet, basename="wishlist")

urlpatterns = [
    path("", include(router.urls)),
]
