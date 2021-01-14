from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import *
import datetime


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "current_bids": Bid.objects.filter(is_current = True)
    })

def category(request, name):
    return render(request, "auctions/index.html", {
        "filter": name,
        "listings": Listing.objects.filter(categories = Category.objects.get(name = name)),
        "current_bids": Bid.objects.filter(is_current = True)
    })

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

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@login_required
def listing(request, title):
    if request.method == 'POST':
        target_listing = Listing.objects.get(title=title)
        if request.POST['action'] == 'Add to Watchlist':
            try:
                target_watchlist = WatchList.objects.get(user = request.user)
                target_watchlist.listings.add(target_listing)
            except WatchList.DoesNotExist:
                new_watchlist = WatchList(user = request.user)
                new_watchlist.save()
                new_watchlist.listings.add(target_listing)
        elif request.POST['action'] == 'Delete from Watchlist':
            try:
                target_watchlist = WatchList.objects.get(user = request.user)
                target_watchlist.listings.remove(target_listing)
            except WatchList.DoesNotExist:
                return HttpResponseBadRequest("Bad Request: watchlist does not exist")
        elif request.POST['action'] == 'Comment':
            new_comment = Comment(listing = target_listing, user = request.user, body = request.POST['body'], date = datetime.datetime.now())
            new_comment.save()
        elif request.POST['action'] == 'Bid':
            previous_bid = Bid.objects.get(listing = target_listing, is_current = True)
            previous_bid.is_current = False
            previous_bid.save()
            new_bid = Bid(listing = target_listing, user = request.user, value = float(request.POST['bid']), date = datetime.datetime.now(), is_current=True)
            new_bid.save()
        elif request.POST['action'] == 'Close Auction':
            target_listing.closed = True
            target_listing.winner = Bid.objects.get(listing = target_listing, is_current = True).user
            target_listing.save()
        return HttpResponseRedirect(reverse("listing", args=(title,)))
    else:
        try:
            listing = Listing.objects.get(title=title)
            comments = Comment.objects.filter(listing=listing)
            current_bid = Bid.objects.get(listing = listing, is_current = True)
            nBids = Bid.objects.filter(listing = listing , is_starting = False).count()
            try:
                watchlist = WatchList.objects.get(user = request.user).listings.all()
            except:
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

@login_required
def create(request):
    if request.method == 'POST':
        category = Category.objects.get(name = request.POST['category'] )
        new_listing = Listing(title = request.POST['title'] , user = request.user, description = request.POST['description'], image = request.POST['image'])
        new_listing.save()
        new_listing.categories.add(category)
        new_bid = Bid(listing = new_listing, user = request.user, value = float(request.POST['starting_bid']), date = datetime.datetime.now(), is_starting=True, is_current=True)
        new_bid.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create.html", {
            "categories": Category.objects.all()
        })

@login_required
def watchlist(request):
    try:
        watchlist = WatchList.objects.get(user = request.user).listings.all()
    except:
        watchlist = []
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist,
        "current_bids": Bid.objects.filter(is_current = True)
    })

@login_required
def myListings(request):
    try:
        listings = Listing.objects.filter(user = request.user)
    except:
        listings = []
    return render(request, "auctions/myListings.html", {
        "listings": listings,
        "current_bids": Bid.objects.filter(is_current = True)
    })