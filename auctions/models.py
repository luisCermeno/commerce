from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"


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

class Comment(models.Model):
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} @ {self.date} on {self.listing} said: {self.body}"