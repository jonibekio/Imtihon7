from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView

from .models import User
from .serializers import UserSerializer


class ProfileUpdateView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'uuid'

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
