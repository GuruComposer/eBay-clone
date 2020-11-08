from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create/", views.Create.as_view(), name="create"),
    path("listing/<int:pk>/", views.ListingDetail.as_view(), name='listing_detail'),
    path("listing/<int:pk>/place_bid", views.PlaceBid.as_view(), name='place_bid'),
    path("listing/<int:pk>/toggle_watchlist", views.ToggleWatchlist.as_view(), name='toggle_watchlist'),
    path("user/watchlist", views.Watchlist.as_view(), name='watchlist'),
    path("listing/<int:pk>/close", views.CloseListing.as_view(), name='close_listing'),
    path("listing/<int:pk>/create_comment", views.CreateComment.as_view(), name='create_comment'),
    path("categories", views.Categories.as_view(), name='categories'),
    path("index/<str:category>", views.Category.as_view(), name='category_view'),
]
