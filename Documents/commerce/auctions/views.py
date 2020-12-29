from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Watchlist, Bids, Comments, Winner

### List of categories we want in the app ###
all_categories = ["Toys","Art","Books","Appliances","Clothing","Sports","Electronics","Other"]

def index(request):


    return render(request, "auctions/index.html", {
        "Listings": Listing.objects.all().filter(open=True),
        "User": User.objects.all()
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


def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        price = request.POST["price"]
        img = request.POST["img"]
        category = request.POST["category"]

        listing = Listing(title=title,description=description,price=price,img=img,category=category,user=request.user)

        listing.save()

        return HttpResponseRedirect(reverse("index"), {

            "title" : title,
            "price" : price,
            "img" : img,
            "category" : category,
            "description" : description
        })
    else:
        return render(request, "auctions/create_listing.html",{
            "categories" : all_categories
        })


def listing(request,listing_id):
    listing = Listing.objects.get(pk=listing_id)

    watchlist_item = Watchlist.objects.filter(user=request.user,listing_id=listing_id)

    owner = (request.user == listing.user)


    if request.method == "POST":
        comment = request.POST.get("comment")

        if (comment):
            comment = Comments(user=request.user,listing_id=listing_id,comments=comment)

            comment.save()

        if (request.POST.get("bid")):

            print(int(request.POST["bid"]))
            bid = int(request.POST["bid"])
            

            if bid > listing.price:

                current_bid = Bids.objects.filter(listing_id=listing_id)

                if current_bid:
                    current_bid.delete()

                new_bid = Bids(title=listing.title,user=request.user,listing_id=listing_id,bid=bid)

                new_bid.save()

                listing = Listing.objects.get(id=listing_id)

                listing.price = bid

                listing.save()

                return render(request,"auctions/listing.html", {
                "listing" : listing,
                "watchlist_item" : watchlist_item ,
                "msg": "You have successfully placed your bid",
                "msg_type": "success",
                "comments": Comments.objects.filter(listing_id=listing_id),
                "owner" : owner
            })
        
            else:
                return render(request,"auctions/listing.html", {
                "listing" : listing,
                "watchlist_item" : watchlist_item ,
                "msg": "Your bid must be greater than the current bid",
                "msg_type": "danger",
                "comments": Comments.objects.filter(listing_id=listing_id),
                "owner" : owner
            })
        else:
            return render(request,"auctions/listing.html", {
            "listing" : listing,
            "watchlist_item" : watchlist_item,
            "comments": Comments.objects.filter(listing_id=listing_id),
            "owner" : owner
        })


    else:
        return render(request,"auctions/listing.html", {
            "listing" : listing,
            "watchlist_item" : watchlist_item,
            "comments": Comments.objects.filter(listing_id=listing_id),
            "owner" : owner
        })

def categories(request):

    if request.method == "POST":

        current_category = request.POST['category']

        listings = Listing.objects.filter(category=current_category,open=True)
        return render(request,"auctions/categories.html", {
            "Listings" : listings,
            "categories" : all_categories,
            "current_category" : current_category
        })

    else:
        return render(request,"auctions/categories.html",{
            "categories" : all_categories
        })

def watchlist(request):
    if request.method == "POST":
        listing_id = request.POST["watchlist"]

        watchlist_item = Watchlist.objects.filter(listing_id=listing_id,user=request.user)

        if not (watchlist_item):

            watchlist = Watchlist(user=request.user,listing_id=listing_id)

            watchlist.save()

            msg = "Added to your watchlist!"
            msg_type = "success"

        else:
            watchlist_item.delete()

            msg = "Deleted from your watchlist!"
            msg_type = "danger"


    watchlist = Watchlist.objects.filter(user=request.user)

    
    items = list(set([item.listing_id for item in watchlist]))

    watchlist = Listing.objects.filter(id__in=items)

    if request.method == "GET":
        return render(request, "auctions/watchlist.html", {
        "watchlist" : watchlist
    })

    else:
        return render(request, "auctions/watchlist.html", {
        "watchlist" : watchlist,
        "msg" : msg,
        "msg_type": msg_type
    })


def closed_listings(request):
    pass
    
    
    # return render(request,"auctions/closed_listings.html",{
    #         "categories" : all_categories
    #     })


def user_listings(request):
    if (request.method == "POST"):
        listing_id = request.POST['close_bid']

        listing = Listing.objects.get(pk=listing_id)

        listing.open = False 

        listing.save()

        owner = request.user

        winner = Bids.objects.get(listing_id=listing_id).user

        winprice = Bids.objects.get(listing_id=listing_id).bid

        title = Bids.objects.get(listing_id=listing_id).title

        winner = Winner(owner=owner,listing_id=listing_id,winner=winner,winprice=winprice,title=title)

        winner.save()


    open_listings = Listing.objects.filter(user=request.user,open=True)

    closed_listings = Listing.objects.filter(user=request.user,open=False)


        

    return render(request,"auctions/user_listings.html",{
            "Open_Listings" : open_listings,
            "Closed_Listings" : closed_listings
        })

        
    
 