from rest_framework.permissions import BasePermission


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        profile = getattr(request.user, "profile", None)
        return bool(profile and profile.role == "seller" and profile.is_verified_seller)
