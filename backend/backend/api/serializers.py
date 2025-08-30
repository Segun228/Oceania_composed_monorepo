from rest_framework import serializers
from .models import Category, Post


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "category", "title", "description", "price", "photos", "weight", "country", "created_at", "updated_at"]
        read_only_fields = ["id", "category", "created_at", "updated_at"]


class CategoryReadSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at", "updated_at", "posts"]
        read_only_fields = ["id", "created_at", "updated_at"]