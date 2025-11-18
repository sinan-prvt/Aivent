from django.urls import path
from apps.categories.views import (
    CategoryListView,
    CategoryCreateView,
    SubCategoryListView,
    SubCategoryCreateView,
)

urlpatterns = [
    path("", CategoryListView.as_view(), name="category-list"),
    path("create/", CategoryCreateView.as_view(), name="category-create"),

    path("<int:category_id>/subcategories/", SubCategoryListView.as_view(), name="subcategory-list"),
    path("subcategories/create/", SubCategoryCreateView.as_view(), name="subcategory-create"),
]
