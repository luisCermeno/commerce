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
        comment = Comment(listing = Listing.objects.get(title=title), user = request.user, body = request.POST['body'], date = datetime.datetime.now(), active = True)
        comment.save()
        return HttpResponseRedirect(reverse("listing", args=(title,)))
        
    else:
        try:
            listing = Listing.objects.get(title=title)
            comments = Comment.objects.filter(listing=listing)

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "datetime": datetime.datetime.now
            })
        except Listing.DoesNotExist:
            return HttpResponseBadRequest("Bad Request: listing does not exist")


def create(request):
    if request.method == 'POST':
        category = Category.objects.get(name = request.POST['category'] )
        new_listing = Listing(title = request.POST['title'] , description = request.POST['description'], image = request.POST['image'])
        new_listing.save()
        new_listing.categories.add(category)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create.html", {
            "categories": Category.objects.all()
        })
