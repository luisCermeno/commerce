from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import *
import datetime

@csrf_exempt
def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "current_bids": Bid.objects.filter(is_current = True)
    })
@csrf_exempt
def category(request, name):
    return render(request, "auctions/index.html", {
        "filter": name,
        "listings": Listing.objects.filter(categories = Category.objects.get(name = name)),
        "current_bids": Bid.objects.filter(is_current = True)
    })
@csrf_exempt
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

@csrf_exempt
@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@csrf_exempt
@login_required
def listing(request, title):
    if request.method == 'POST':
        # Get the object for that listing
        target_listing = Listing.objects.get(title=title)

        # Determine which action the user is intending to do
        if request.POST['action'] == 'Add to Watchlist':
            try:
                # Get the watchlist object for that user
                target_watchlist = WatchList.objects.get(user = request.user)
                # Add the listing to that watchlist 
                target_watchlist.listings.add(target_listing)
            except WatchList.DoesNotExist:
                # If the watchlist does not exist yet, create it
                new_watchlist = WatchList(user = request.user)
                new_watchlist.save()
                # Add the listing to that watchlist 
                new_watchlist.listings.add(target_listing)

        elif request.POST['action'] == 'Delete from Watchlist':
            try:
                # Get the watchlist object for that user
                target_watchlist = WatchList.objects.get(user = request.user)
                # Remove the listing to that watchlist 
                target_watchlist.listings.remove(target_listing)
            except WatchList.DoesNotExist:
                # If the watchlist does not exist yet, display an error
                return HttpResponseBadRequest("Bad Request: watchlist does not exist")

        elif request.POST['action'] == 'Comment':
            # Create a new comment object and save it.
            new_comment = Comment(listing = target_listing, user = request.user, body = request.POST['body'], date = datetime.datetime.now())
            new_comment.save()

        elif request.POST['action'] == 'Bid':
            # Get the bid previous to the new bid made by the user
            previous_bid = Bid.objects.get(listing = target_listing, is_current = True)
            # Set its current field to false and save it
            previous_bid.is_current = False
            previous_bid.save()
            # Create new bid with current field set to true and save it
            new_bid = Bid(listing = target_listing, user = request.user, value = float(request.POST['bid']), date = datetime.datetime.now(), is_current=True)
            new_bid.save()

        elif request.POST['action'] == 'Close Auction':
            # Set the listing's close field to True
            target_listing.closed = True
            # Set the listing's winner field to the user who made the latest bid, and save
            target_listing.winner = Bid.objects.get(listing = target_listing, is_current = True).user
            target_listing.save()
        return HttpResponseRedirect(reverse("listing", args=(title,)))
    else:
        try:
            # Get listing, comment, bid objects and count the number of bid objects which is_starting field
            # is set to False
            listing = Listing.objects.get(title=title)
            comments = Comment.objects.filter(listing=listing)
            current_bid = Bid.objects.get(listing = listing, is_current = True)
            nBids = Bid.objects.filter(listing = listing , is_starting = False).count()
            try:
                # Try to get the watchlist for that user
                watchlist = WatchList.objects.get(user = request.user).listings.all()
            except:
                # If the user does not have a watchlist, set it to an empty list
                watchlist = []
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "current_bid": current_bid,
                "nBids": nBids,
                "watchlist": watchlist,
                "datetime": datetime.datetime.now,
                "bid_limit": float(current_bid.value) + 0.01
            })
        except Listing.DoesNotExist:
            return HttpResponseBadRequest("Bad Request: listing does not exist")

@csrf_exempt
@login_required
def create(request):
    if request.method == 'POST':
        # Create a new Listing object
        new_listing = Listing(title = request.POST['title'] , user = request.user, description = request.POST['description'], image = request.POST['image'])
        new_listing.save()
        # Get the category the user selected and add it to the categories field of the newly created listing
        category = Category.objects.get(name = request.POST['category'] )
        new_listing.categories.add(category)
        # Create a new bid with is_starting field set to true which indicates it is the starting bid set by the user
        new_bid = Bid(listing = new_listing, user = request.user, value = float(request.POST['starting_bid']), date = datetime.datetime.now(), is_starting=True, is_current=True)
        new_bid.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create.html", {
            "categories": Category.objects.all()
        })

@csrf_exempt
@login_required
def watchlist(request):
    try:
        # Try to get the watchlist for that user
        watchlist = WatchList.objects.get(user = request.user).listings.all()
    except:
        # If the user does not have a watchlist, set it to an empty list
        watchlist = []
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist,
        "current_bids": Bid.objects.filter(is_current = True)
    })

@csrf_exempt
@login_required
def myListings(request):
    try:
        # Try to get the listings which user field is the user who made the request
        listings = Listing.objects.filter(user = request.user)
    except:
         # If there are no matches, set it to an empty list
        listings = []
    return render(request, "auctions/myListings.html", {
        "listings": listings,
        "current_bids": Bid.objects.filter(is_current = True)
    })