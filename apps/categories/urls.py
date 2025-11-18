from django.urls import path
from apps.categories.views import (
    CategoryListView,
    CategoryCreateView,
    SubCategoryListView,
    SubCategoryCreateView,
)

urlpattern = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/create/", CategoryCreateView.as_view(), name="category-create"),

    path("categories/<int:category_id>/subcategories/", SubCategoryListView.as_view(), name="subcategory-list"),
    path("subcategories/create/", SubCategoryCreateView.as_view(), name="subcategory-create"),
]