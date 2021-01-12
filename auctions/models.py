from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"


class Category(models.Model): 
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    user = models.ForeignKey(User, default=1 , on_delete=models.CASCADE, related_name='listings')
    categories = models.ManyToManyField(Category, blank=True, related_name="listings")
    description = models.CharField(max_length=500)
    image = models.URLField(max_length=200, blank=True)
    highest_bid = models.DecimalField(decimal_places=2, max_digits=9, default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.title}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} @ {self.date} on {self.listing} said: {self.body}"

class Bid(models.Model):
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE,related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    value = models.DecimalField(decimal_places=2, max_digits=9, default=0, validators=[MinValueValidator(0)])
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} @ {self.date} on {self.listing} bid: $ {self.value}"

class WatchList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='watchlist')
    listings = models.ManyToManyField(Listing, blank=True, related_name='listings')

    def __str__(self):
        return f"{self.user}'s Watch List"