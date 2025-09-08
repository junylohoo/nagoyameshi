from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string
from django.conf import settings
import os

def create_id():
    return get_random_string(22)

def upload_image_to(instance, filename):
    item_id = instance.id
    return os.path.join('items', item_id, filename)


class Tag(models.Model):
    slug = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Category(models.Model):
    slug = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Item(models.Model):
    id = models.CharField(default=create_id, primary_key=True, max_length=22, editable=False)
    name = models.CharField(default='', max_length=50)
    description = models.TextField(default='', blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(default="", blank=True, upload_to=upload_image_to)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag)  # 中間テーブルは自動生成
    address = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=20, default='')

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.item}"
    
class Review(models.Model):
    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="reviews")
    title = models.CharField(max_length=100, default="")
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
            return f"{self.title} - {self.user}"
    
    
class Reservation(models.Model):
        user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        item = models.ForeignKey(Item, on_delete=models.CASCADE)
        reserved_at = models.DateTimeField(auto_now_add=True)

def __str__(self):
        return f"{self.user.username} - {self.item.name}"


