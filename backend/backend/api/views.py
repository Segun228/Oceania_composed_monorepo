from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Post, Category
from .serializers import (
    PostSerializer,
    CategoryReadSerializer,
    CategorySerializer
)

from .permissions import IsAdminOrDebugOrReadOnly


# ===== Category Views =====

class CategoryListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminOrDebugOrReadOnly]
    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CategoryReadSerializer
        return CategorySerializer


class CategoryRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrDebugOrReadOnly]
    queryset = Category.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'category_id'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CategoryReadSerializer
        return CategorySerializer


# ===== Post Views =====

class PostListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminOrDebugOrReadOnly]
    serializer_class = PostSerializer

    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        return Post.objects.filter(category__id=category_id)

    def perform_create(self, serializer):
        category = get_object_or_404(Category, pk=self.kwargs['category_id'])
        serializer.save(category=category)


class PostRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrDebugOrReadOnly]
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = 'post_id'

    def get_object(self):
        queryset = self.get_queryset()
        category_id = self.kwargs.get("category_id")
        post_id = self.kwargs.get("post_id")
        obj = get_object_or_404(queryset, pk=post_id, category__id=category_id)
        self.check_object_permissions(self.request, obj)
        return obj
