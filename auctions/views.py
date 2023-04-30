from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, Listing, Bid, Comment,Category
from django.db.models import Max
from decimal import Decimal

class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('category', 'title', 'description', 'start_amount', 'photo',)
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'start_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'})
        }


class BidInputForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ('bid_amount',)
        widgets = {
            'bid_amount': forms.NumberInput(attrs={'class': 'form-control'})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment',)
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control'})
        }


def index(request): # returns list of Active Listings w/ attributes
    return render(request, "auctions/index.html",{
        "listings": Listing.objects.filter(close_listing=False)
    })


def view_listing(request, id): # Displays page of selected Listing
    listing= Listing.objects.get(pk=id)
    highest_bid = Bid.objects.filter(listing_id=id).aggregate(Max('bid_amount'))['bid_amount__max']  or Decimal('0')
    addedtowatchlist = False
    closelistingbutton = False
    won = False 
    current_highest_bid = highest_bid if highest_bid > listing.start_amount else listing.start_amount
    viewmessage = f'Enter amount higher than US${round(current_highest_bid,2)}'
    winmessage = ""
    if request.user.is_authenticated:
        if listing.seller == request.user: # If the user created the listing, close button will appear on the page
            closelistingbutton = True

        if request.user in listing.watchlist.all(): # Checks if user has already added listing to watchlist
            addedtowatchlist = True

        if Bid.objects.filter(bidder=request.user, listing_id=id).exists(): # If the user has already placed a bid
            if (Bid.objects.get(bidder=request.user, listing_id=id).bid_amount == current_highest_bid): # If the user has the highest bid
                viewmessage = f'Your (${round(current_highest_bid, 2)}) bid is the current bid.'
        
        if listing.close_listing == True:# If Listing was  already closed
            if Bid.objects.filter(listing_id=id).exists():
                highest_bidder = Bid.objects.get(listing_id=id, bid_amount=current_highest_bid).bidder
                won = True
                if highest_bidder == request.user: #user has won the bidding
                    winmessage = "You won!"
                else:
                    winmessage = f'{highest_bidder} has won the bidding!'
                
                return render(request,"auctions/view_listing.html", {
                    "listing": listing, 
                    "comments": Comment.objects.filter(listing_id=id),
                    "addedtowatchlist": addedtowatchlist,
                    "winmessage": winmessage,
                    "won": True
                })
    return render(request,"auctions/view_listing.html", {
        "listing": listing,
        "bidcount": Bid.objects.filter(listing_id=id).count(),
        "form": BidInputForm(),
        "viewmessage": viewmessage,
        "comments": Comment.objects.filter(listing_id=id),
        "commentForm": CommentForm(),
        "addedtowatchlist": addedtowatchlist,
        "closelistingbutton": closelistingbutton
    })


@login_required
def create_listing(request): #Create listing through a Form Input
    if request.method == 'POST':
            form= CreateListingForm(request.POST, request.FILES)
            if form.is_valid():
                obj = Listing() #saving user input to database
                obj.seller = request.user
                obj.category = form.cleaned_data['category']
                obj.title = form.cleaned_data['title']
                obj.description = form.cleaned_data['description']
                obj.start_amount = form.cleaned_data['start_amount']
                obj.photo = form.cleaned_data['photo']
                obj.save()
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "auctions/create_listing.html",{
                "form": form
                })
    return render(request, "auctions/create_listing.html",{
            "form": CreateListingForm() # creates a blank form
    })

@login_required
def bid_listing(request, id): # Bids listing Feature
    listing= Listing.objects.get(pk=id)
    addedtowatchlist = False
    # aggregate(Max('bid_amount') gets MAX value given the id - listing.
    # ['bid_amount__max'] to get value from the dictionary {'bid_amount__max': Decimal('value')}/ value = dict['key]
    # Decimal('0') -> if theres no bid yet, so it won't return None
    highest_bid = Bid.objects.filter(listing_id=id).aggregate(Max('bid_amount'))['bid_amount__max']  or Decimal('0')
    if request.method == 'POST': 
        form= BidInputForm(request.POST)
        if form.is_valid():
            current_bid = form.cleaned_data['bid_amount']
            message = listing.start_amount if listing.start_amount > highest_bid else highest_bid 

            if request.user in listing.watchlist.all(): # Checks if user has already added listing to watchlist
                addedtowatchlist = True
            if (current_bid > listing.start_amount and current_bid > highest_bid):
                if Bid.objects.filter(bidder=request.user, listing_id=id).exists(): #update bid if user has alreadt placed bid previously
                    obj= Bid.objects.get(bidder=request.user, listing_id=id)
                else:
                    obj = Bid()
                obj.listing = listing
                obj.bidder = request.user
                obj.bid_amount = current_bid
                obj.save()
                message = highest_bid
                return render(request,"auctions/view_listing.html", {
                    "listing": listing, 
                    "bidcount": Bid.objects.filter(listing_id=id).count(),
                    "form": BidInputForm(),
                    "bidsuccess": "Bid Placed Successfully.",
                    "viewmessage": f'Enter amount higher than US${current_bid}',
                    "comments": Comment.objects.filter(listing_id=id),
                    "addedtowatchlist": addedtowatchlist,
                    "commentForm": CommentForm()
                })

            else:
                return render(request,"auctions/view_listing.html", {
                    "listing": listing, 
                    "bidcount": Bid.objects.filter(listing_id=id).count(),
                    "form": form,
                    "biderror": f'You have to bid more than US ${round(message,2)}!',
                    "comments": Comment.objects.filter(listing_id=id),
                    "addedtowatchlist": addedtowatchlist,
                    "commentForm": CommentForm()
                })
        else:
            return render(request, "auctions/view_listing.html",{
                "form": form
            })


@login_required
def comment(request, id): # Adds a comment on a listing
    listing= Listing.objects.get(pk=id)
    if request.method == 'POST':
        form= CommentForm(request.POST)
        if form.is_valid():
            obj = Comment() #saving
            obj.listing = listing
            obj.commented_by = request.user
            obj.comment = form.cleaned_data['comment']
            obj.save()
            return HttpResponseRedirect(reverse("view_listing",args=(id,)))
        else:
            return render(request, "auctions/view_listing.html",{
                "form": form
            })

@login_required
def close_listing(request, id): # Close listing by seller/current user
    listing= Listing.objects.get(pk=id)
    if listing.seller == request.user:
        listing.close_listing = True
        listing.save()
        return HttpResponseRedirect(reverse("view_listing",args=(id,)))


def categories(request): # Displays List of Categories (Category Page)
    return render(request, "auctions/category.html",{
        "categories": Category.objects.all()
    })    


def view_category(request, id): # Displays all Listings per selected category
    return render(request, "auctions/index.html", {
        "category": Category.objects.get(pk=id),
        "categorylist" : True,
        "listings": Listing.objects.filter(category_id=id).exclude(close_listing=True)
    })

@login_required
def bids(request): # Added extra feature for the user to monitor items that he/she has bid, Displays Bid Page
    # Only filter the list of IDs - Listing that that the current user bid
    list_ids = Bid.objects.filter(bidder=request.user).values_list('listing_id', flat=True)
    return render(request, "auctions/index.html",{
        "listings": Listing.objects.filter(pk__in=list_ids),
        "bids": True
    })

@login_required
def watchlists(request): # Displays watchlisted listings on Watchlist Page
    return render(request, "auctions/index.html",{
        "listings": request.user.watchlist.all(),
        "watchlist": True
    })


def add_to_watchlist(request, id): # Add current listing to watchlist
    listings= Listing.objects.get(pk=id)
    if request.user.is_authenticated:
        if request.POST.get("addwatchlist"): 
            listings.watchlist.add(request.user) # Add listing to watchlist
        elif request.POST.get("removewatchlist"):
            listings.watchlist.remove(request.user) # Remove listing from watchlist  
        return HttpResponseRedirect(reverse("view_listing",args=(id,)))
    else:
        return HttpResponseRedirect(reverse("login"))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
