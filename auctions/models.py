from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    categories = models.ManyToManyField(Category, blank=True, related_name="listings")
    description = models.CharField(max_length=500)
    image = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.title}"