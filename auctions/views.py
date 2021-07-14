from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max


from .models import User, Listing, Bid, Comment


def index(request):
    all_listing = Listing.objects.filter(status=True)
    return render(request, "auctions/index.html", {
        "listing": all_listing,
    })

@login_required
def categories(request):
    return render(request, "auctions/category.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
            request.session["username"] = request.POST["username"]
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
        request.session["username"] = username
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        startBiding = request.POST["startBid"]
        image = request.POST["image_url"]
        try:
            category = request.POST["category"]
        except KeyError:
            category = "Other"
        user = User.objects.get(username=request.session["username"])
        # Attempt to create new listing
        try:
            listing = Listing(title=title, description=description, image=image, category=category, highest_bid=startBiding, user_id=user)
            listing.save()
            biding = Bid(biding=startBiding, user_id=user, listing_id=listing)
            biding.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/listing.html")

@login_required
def listing(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id)
        user = User.objects.get(username=request.session["username"])
        comment = Comment.objects.filter(listing_id=listing_id).order_by('-id')
        bid = Bid.objects.filter(listing_id=listing_id).order_by('biding').last()
        countbid = Bid.objects.filter(listing_id=listing_id).count()
        countbid = countbid - 1
        watchlist = listing.watchlist.filter(username=request.session["username"]).count()
        request.session["countbid"] = countbid

    except Listing.DoesNotExist:
        return HttpResponseBadRequest("Bad Request: no flight chosen")
    return render(request, "auctions/list.html", {
        "listing": listing, 
        "bid": bid, 
        "countbid":countbid, 
        "comment":comment,
        "userName":request.session["username"],
        "watchlist": watchlist
    })

@login_required
def place_bid(request):
    placed_bid = request.POST["bid"]
    listing_id = request.POST["listing_id"]
    listing = Listing.objects.get(id=listing_id)
    comment = Comment.objects.filter(listing_id=listing_id).order_by('-id')
    user = User.objects.get(username=request.session["username"])
    bid = Bid.objects.filter(listing_id=listing_id).order_by('biding').last()
    watchlist = listing.watchlist.filter(username=request.session["username"]).count()

    if int(placed_bid) > int(bid.biding):
        biding = Bid(biding=placed_bid, user_id=user, listing_id=listing)
        listing.highest_bid = placed_bid
        listing.save()
        biding.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id] ))
    else:
        return render(request, "auctions/list.html", {
            "listing": listing, 
            "bid":bid,
            "countbid": request.session["countbid"],
            "comment":comment,
            "userName":request.session["username"],
            "message_biding": "Your bid should be higuer than the current bid.",
            "watchlist": watchlist

        })

@login_required
def watchlist(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(id=listing_id)
        user = User.objects.get(username=request.session["username"])

        listing.watchlist.add(user)
        return HttpResponseRedirect(reverse("listing", args=[listing_id] ))
    else:
        user = User.objects.get(username=request.session["username"])
        return render(request, "auctions/watchlist.html", {
            "listing": user.watchlist.all(),
        })

@login_required
def removeWatchlist(request):
    listing_id = request.POST["listing_id"]
    listing = Listing.objects.get(id=listing_id)
    user = User.objects.get(username=request.session["username"])

    listing.watchlist.remove(user)
    return HttpResponseRedirect(reverse("listing", args=[listing_id] ))


@login_required
def category(request, search):
    all_listing = Listing.objects.all()
    listing = all_listing.filter(category__contains=search)
    return render(request, "auctions/category.html", {
        "listing": listing,
    })

@login_required
def comment(request):
    comment = request.POST["comment"]
    listing_id = request.POST["listing_id"]
    comments = Comment.objects.filter(listing_id=listing_id).order_by('-id')
    listing = Listing.objects.get(id=listing_id)
    user = User.objects.get(username=request.session["username"])
    bid = Bid.objects.filter(listing_id=listing_id).order_by('biding').last()
    
    if comment:
        comment = Comment(comment=comment, user_id=user, listing_id=listing)
        comment.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id] ))
    else:
        return render(request, "auctions/list.html", {
            "listing": listing, 
            "bid":bid,
            "countbid": request.session["countbid"],
            "comment":comments,
            "userName":request.session["username"],
            "message_comment": "Your comment cant be empty."
        })

@login_required
def close(request):
    listing_id = request.POST["listing_id"]
    comments = Comment.objects.filter(listing_id=listing_id).order_by('-id')
    listing = Listing.objects.filter(id=listing_id).update(status=False)
    user = User.objects.get(username=request.session["username"])
    bid = Bid.objects.filter(listing_id=listing_id).order_by('biding').last()

    return HttpResponseRedirect(reverse("listing", args=[listing_id] ))