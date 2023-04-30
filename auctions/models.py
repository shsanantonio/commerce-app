from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Create your models here.

class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return f'{self.category}'


class Listing(models.Model):
    seller = models.ForeignKey("User", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listingcategory", null = True, blank=True )
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1024)
    start_amount = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to="media", blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)
    close_listing = models.BooleanField(default=False)
    watchlist = models.ManyToManyField("User", related_name="watchlist", default=None, blank=True)

    def __str__(self):
        return f'{self.title} (${self.start_amount})'

    @property
    def get_photo_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url


class Bid(models.Model):
    bidder = models.ForeignKey("User", on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bidding")
    bid_amount = models.DecimalField(max_digits=10,decimal_places=2)
    
    def __str__(self):
        return f'{self.listing_id} {self.bidder.username} ${self.bid_amount}'


class Comment(models.Model):
    commented_by = models.ForeignKey("User", on_delete=models.CASCADE)
    listing= models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=256)
    date_added = models.DateTimeField(default=timezone.now)

