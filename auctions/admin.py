from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . models import Category, Listing, Bid, Comment, User

# Register your models here.
class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "seller", "category", "title", "description", "start_amount", "photo", "close_listing",)
    filter_horizontal = ("watchlist",)

    list_filter = ["seller"]

class BidAdmin(admin.ModelAdmin):
    list_display = ("listing_id", "listing", "bid_amount", "bidder")
    list_filter = ["bidder"]

class CommentAdmin(admin.ModelAdmin):
    list_display = ("comment",  "commented_by", "listing", "date_added")
    list_filter = ["commented_by"]

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("category",)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Listing,ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User, UserAdmin)

