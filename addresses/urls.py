from django.urls import include, path
from rest_framework.routers import DefaultRouter

from addresses.views import UserAddressViewSet

router = DefaultRouter()
router.register("addresses", UserAddressViewSet, basename="address")

urlpatterns = [
    path("", include(router.urls)),
]
