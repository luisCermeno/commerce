from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from .models import *
from django import forms
import datetime


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
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
            new_comment = Comment(listing = target_listing, user = request.user, body = request.POST['body'], date = datetime.datetime.now(), active = True)
            new_comment.save()
        elif request.POST['action'] == 'Bid':
            new_bid = Bid(listing = target_listing, user = request.user, value = float(request.POST['bid']), date = datetime.datetime.now(), active = True)
            new_bid.save()
            target_listing.highest_bid = float(new_bid.value)
            target_listing.save()
        return HttpResponseRedirect(reverse("listing", args=(title,)))
    else:
        try:
            listing = Listing.objects.get(title=title)
            comments = Comment.objects.filter(listing=listing)
            watchlist = WatchList.objects.get(user = request.user).listings.all()
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "watchlist": watchlist,
                "datetime": datetime.datetime.now,
                "bid_limit": float(listing.highest_bid) + 0.01
            })
        except Listing.DoesNotExist:
            return HttpResponseBadRequest("Bad Request: listing does not exist")


def create(request):
    if request.method == 'POST':
        category = Category.objects.get(name = request.POST['category'] )
        new_listing = Listing(title = request.POST['title'] , description = request.POST['description'], image = request.POST['image'], highest_bid = float(request.POST['starting_bid']) )
        new_listing.save()
        new_listing.categories.add(category)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create.html", {
            "categories": Category.objects.all()
        })
