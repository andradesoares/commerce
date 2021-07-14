from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("categories/<str:search>", views.category, name="category"),
    path("categories", views.categories, name="categories"),
    path("place_bid", views.place_bid, name="place_bid"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("removeWatchlist", views.removeWatchlist, name="removeWatchlist"),
    path("comment", views.comment, name="comment"),
    path("close", views.close, name="close"),
]
