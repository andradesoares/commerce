from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listing(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    category = models.CharField(max_length=32, blank=True)
    image = models.CharField(max_length=64, blank=True)
    status = models.BooleanField(default=True)
    highest_bid = models.IntegerField(blank=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="list")
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")

class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    biding = models.IntegerField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid")
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid")

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=256)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment")
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment")