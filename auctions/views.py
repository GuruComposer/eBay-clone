from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from .forms import NewListingForm, NewBidForm, NewCommentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max, Count

from .models import User, Listing, Comment


### delete this method and refactor views for "listing_page_utility"
# def highest_bid_price_utility(self, pk):
#     listing = Listing.objects.get(id=pk)
#     if listing.num_bids > 0:
#         highest_bid = listing.highest_bid()
#     else: 
#         highest_bid = None
#     return highest_bid

### delete this method and refactor views for "listing_page_utility"
# def is_in_watchlist(request, pk):
#     listing = Listing.objects.get(id=pk)
#     if request.user.is_authenticated:
#         in_watchlist = listing in request.user.watchlist.all()
#     else:
#         in_watchlist = False
#     return in_watchlist

def listing_page_utility(request, listing_id, **kwargs):
    listing = Listing.objects.annotate(highest_bid_price=Max('bids__bid_price')).get(id=listing_id)
    # comments = Comment.objects.filter(listing=listing)
    message = kwargs.get('message', None)
    comments = Comment.objects.filter(listing=listing)
    
    if request.user.is_authenticated:
        in_watchlist = listing in request.user.watchlist.all()
    else:
        in_watchlist = False
    
    return listing, in_watchlist, message, comments



def index(request):
    listings = Listing.objects.annotate(highest_bid_price=Max('bids__bid_price')) # .filter(active=True)
    count = Listing.objects.all().count()
    ctx =   {'listings': listings, 
            'count': count,
            'page': 'active_listings',}
    return render(request, "auctions/index.html", ctx)


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

class Create(LoginRequiredMixin, View):
    template = 'auctions/create.html'
    success_url = reverse_lazy('index')
    def get(self, request):
        form = NewListingForm()
        ctx = {'form': form}
        return render(request, self.template, ctx)

    def post(self, request):
        form = NewListingForm(request.POST)
        if  form.is_valid():
            form.instance.owner = request.user
            form.save()
            return redirect(self.success_url)
        else:
            ctx = {'form': form}
            return render(request, self.template, ctx)

class ListingDetail(View):
    template_name = "auctions/listing_detail.html"
    def get(self, request, pk):
        listing, in_watchlist, message, comments = listing_page_utility(request, pk)
        bid_form = NewBidForm()
        comment_form = NewCommentForm()
        ctx =   {'listing': listing,
                'bid_form': bid_form,
                'comment_form': comment_form,
                'in_watchlist': in_watchlist,
                'message': message,
                'comments': comments}
        return render(request, self.template_name, ctx)

class PlaceBid(LoginRequiredMixin, View):
    template_name = "auctions/listing_detail.html"
    def post(self, request, pk):
        bid_form = NewBidForm(request.POST)
        listing, in_watchlist, message, comments = listing_page_utility(request, pk)
        success_url = reverse('listing_detail', args=[pk])

        if bid_form.is_valid():
            bid_form.instance.owner = request.user
            bid_form.instance.listing = listing
            bid_price = bid_form.instance.bid_price
            if bid_price < listing.highest_bid() or bid_price < listing.starting_price:
                message = "* Your bid was not high enough."
                ctx =   {'listing': listing,
                        'bid_form': bid_form,
                        'message': message,
                        'pk': pk,
                        'in_watchlist': in_watchlist,
                        'comment_form': NewCommentForm(),
                        'message': message,
                        'comments': comments}
                return render(request, 'auctions/listing_detail.html', ctx)
            else:
                bid_form.save()
                count = listing.bids.all().count()
                listing.num_bids = count
                listing.save()
                return HttpResponseRedirect(success_url)
        else:
            ctx =   {'listing': listing,
                    'bid_form': bid_form,}
            return render(request, self.template_name, ctx)

class ToggleWatchlist(LoginRequiredMixin, View):
    def post(self, request, pk):
        listing, in_watchlist, message, comments = listing_page_utility(request, pk)
        user = request.user

        if in_watchlist:
            user.watchlist.remove(listing)
        else:
            user.watchlist.add(listing)
        return HttpResponseRedirect(reverse('listing_detail', args=[pk]))

class Watchlist(LoginRequiredMixin, View):
    def get(self, request):
        listings = request.user.watchlist.all()
        listings = listings.annotate(highest_bid_price=Max('bids__bid_price'))
        count = Listing.objects.all().count()
        ctx =   {'listings': listings,
                'count': count,
                'page': 'watchlist',}
        return render(request, "auctions/index.html", ctx)

class CloseListing(LoginRequiredMixin, View):
    def post(self, request, pk):
        listing, in_watchlist, message, comments = listing_page_utility(request, pk)
        if request.user == listing.owner:
            listing.active = False
            bids = listing.bids.all().order_by('-bid_price')
            highest_bid = bids[0]
            listing.winner = highest_bid.owner
            listing.save()
            return HttpResponse("good job")

class CreateComment(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment_form = NewCommentForm(request.POST)
        listing, in_watchlist, message, comments = listing_page_utility(request, pk)
        success_url = reverse('listing_detail', args=[pk])
                        
        if comment_form.is_valid():
            comment_form.instance.owner = request.user
            comment_form.instance.listing = listing
            comment_form.save()
            return HttpResponseRedirect(success_url)
        else:
            bid_form = NewBidForm()
            message = 'Invalid comment.'
            ctx = {
                'listing': listing,
                'bid_form': bid_form,
                'comment_form': comment_form,
                'in_watchlist': in_watchlist,
                'message': message,
            }   
            return render(request, 'auctions/listing_detail.html', ctx)

class Categories(View):
    def get(self, request):
        categories = Listing.objects.filter(active=True).order_by("category").values_list("category", flat=True).distinct()
        categories = [category.capitalize() for category in categories if category is not None]
        print(categories)
        ctx = {
            'categories': categories
        }
        return render(request, 'auctions/categories.html', ctx)

class Category(View):
    def get(self, request, category):
        listings = Listing.objects.filter(category=category.upper()).filter(active=True)
        ctx = {
            'category': category,
            'listings': listings,
            'page': 'category'
        }
        return render(request, 'auctions/index.html', ctx)






