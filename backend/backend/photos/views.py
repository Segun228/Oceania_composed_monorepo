from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import AllowAny

from .models import Post

from .serializers import (
    PostSerializer
)

from .permissions import PhotoIsAdminOrDebugOrReadOnly


class PhotosView(RetrieveUpdateDestroyAPIView):
    permission_classes = [PhotoIsAdminOrDebugOrReadOnly]
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = 'post_id'
    http_method_names = ['get', 'patch']