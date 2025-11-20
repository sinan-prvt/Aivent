
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.categories.models import Category, SubCategory
from apps.categories.serializers import CategorySerializer, SubCategorySerializer
from apps.users.permissions import IsAdmin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="List categories",
        tags=["Categories"]
    )
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CategoryCreateView(generics.CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        operation_description="Create category",
        tags=["Categories"]
    )

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SubCategoryListView(generics.ListAPIView):
    serializer_class = SubCategorySerializer

    @swagger_auto_schema(
        operation_description="List subcategories of a category",
        tags=["Categories"]
    )

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        return SubCategory.objects.filter(category_id=category_id)


class SubCategoryCreateView(generics.CreateAPIView):
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        operation_description="Create subcategory",
        tags=["Categories"]
    )

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)