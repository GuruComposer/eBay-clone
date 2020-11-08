from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator


class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing", blank=True, related_name="watchlist")

class Listing(models.Model):
    def highest_bid(self):
        print(self.bids.all().count() == 0)
        if self.bids.all().count() == 0:
            return 0
        else:
            highest_bid = self.bids.order_by('bid_price').last().bid_price
            return highest_bid

    CATEGORY_LIST = [
            ('BOOKS', 'Books'),
            ('MUSIC', 'Music'),
            ('MOVIES', 'Movies'),
            ('GAMES', 'Games'),
            ('COMPUTERS', 'Computers'),
            ('ELECTRONICS', 'Electronics'),
            ('KITCHEN', 'Kitchen'),
            ('HOME', 'Home'),
            ('HEALTH', 'Health'),
            ('PETS', 'Pets'),
            ('TOYS', 'Toys'),
            ('FASHION', 'Fashion'),
            ('SHOES', 'Shoes'),
            ('SPORTS', 'Sports'),
            ('BABY', 'Baby'),
            ('TRAVEL', 'Travel')
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings", null=True)
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2, "Title must be greater than 2 chracters")],
        verbose_name="Title"
    )
    description = models.TextField(verbose_name="Description")
    category = models.CharField(choices=CATEGORY_LIST, blank=True, max_length=100, null=True)
    starting_price = models.DecimalField(decimal_places=2, verbose_name="Starting Price", max_digits=10)
    image = models.URLField(blank=True, verbose_name="Image URL", null=True)
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    num_bids = models.PositiveIntegerField(default=0, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids", null=True, blank=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", null=True)
    bid_price = models.DecimalField(decimal_places=2, verbose_name="Bid Price", max_digits=10, null=True)
    bid_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.owner} bid ${self.bid_price} for: {self.listing} at {self.bid_time}."

class Comment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments", null=True)
    text = models.TextField(max_length=200, verbose_name="comment", default="", null=True)
    time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.owner}: {self.text} --- "

