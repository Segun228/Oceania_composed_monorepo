from django.urls import path
from api.views import (
    PostRetrieveUpdateDestroyView,
    PostListCreateView,
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView
)


urlpatterns = [
    path('categories/<int:category_id>/posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('categories/<int:category_id>/posts/<int:post_id>/', PostRetrieveUpdateDestroyView.as_view(), name='post-update-destroy'),

    path('categories/', CategoryListCreateView.as_view(), name='categories-list'),
    path('categories/<int:category_id>/', CategoryRetrieveUpdateDestroyView.as_view(), name='categories-detail'),
]