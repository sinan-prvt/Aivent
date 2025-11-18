
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.categories.models import Category, SubCategory
from apps.categories.serializers import CategorySerializer, SubCategorySerializer
from apps.users.permissions import IsAdmin


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class CategoryCreateView(generics.CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class SubCategoryListView(generics.ListAPIView):
    serializer_class = SubCategorySerializer

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        return SubCategory.objects.filter(category_id=category_id)


class SubCategoryCreateView(generics.CreateAPIView):
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]
