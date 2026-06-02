from rest_framework.viewsets import ReadOnlyModelViewSet

from categories.models import Category
from categories.serializers import CategorySerializer


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.select_related("parent").order_by("name")
    serializer_class = CategorySerializer
    lookup_field = "slug"
