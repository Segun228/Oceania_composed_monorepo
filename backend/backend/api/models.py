from django.db import models
from authentication.models import User
from django.contrib.postgres.fields import ArrayField


class Category(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, default="Раздел", unique= True)
    description = models.CharField(max_length=1000, null=True, blank=False, default="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'раздел объявлений'
        verbose_name_plural = 'разделы объявлений'

    def __str__(self):
        return self.name


class Post(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True, default="")
    price = models.IntegerField(default=0)
    photos = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    weight = models.IntegerField(default=0)
    country = models.CharField(max_length=1000, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'объявление'
        verbose_name_plural = 'объявления'

    def __str__(self):
        return self.title
