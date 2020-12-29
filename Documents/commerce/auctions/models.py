from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
   title = models.CharField(max_length=64)
   description = models.CharField(max_length= 264)
   price = models.IntegerField()
   user = models.CharField(max_length=64)
   date = models.DateTimeField(auto_now=False, auto_now_add=True)
   img = models.CharField(max_length = 264,blank=True)
   category = models.CharField(max_length=64,blank=True)
   open = models.BooleanField(default=True)


   def __str__(self):
       return f"{self.title} is currently ${self.price} with the id {self.id} at {self.date}"
   


class Bids(models.Model):
    user = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    listing_id = models.IntegerField()
    bid = models.IntegerField()



class Comments(models.Model):
    user = models.CharField(max_length=64)
    comments = models.CharField(max_length=264)
    listing_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Watchlist(models.Model):
    user = models.CharField(max_length=64)
    listing_id = models.IntegerField()

class Winner(models.Model):
    owner = models.CharField(max_length=64)
    winner = models.CharField(max_length=64)
    listing_id = models.IntegerField()
    winprice = models.IntegerField()
    title = models.CharField(max_length=64, null=True)


