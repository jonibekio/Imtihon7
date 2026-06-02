from django.urls import include, path
from rest_framework.routers import DefaultRouter

from profiles.views import ProfileViewSet

router = DefaultRouter()
router.register("profiles", ProfileViewSet, basename="profile")

urlpatterns = [
    path("", include(router.urls)),
]
