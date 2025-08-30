from django.urls import path
from .views import AddPostsFile, ReplacePostsFile, GetPostsFile

urlpatterns = [
    path("current/add/", AddPostsFile.as_view(), name="add-posts-endpoint"),
    path("current/replace/", ReplacePostsFile.as_view(), name="replace-posts-endpoint"),
    path("current/", GetPostsFile.as_view(), name="get-table-endpoint"),
]