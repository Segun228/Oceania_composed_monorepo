from django.contrib import admin
from django.urls import path

from .views import PhotosView


urlpatterns = [
    path("<int:post_id>/", PhotosView.as_view(), name="photo endpoint"),
]