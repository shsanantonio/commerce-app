from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("view_listing/<int:id>", views.view_listing, name="view_listing"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("bid_listing/<int:id>", views.bid_listing, name="bid_listing"),
    path("comment/<int:id>", views.comment, name="comment"),
    path("close_listing/<int:id>", views.close_listing, name="close_listing"),
    path("categories", views.categories, name="categories"),
    path("view_category/<int:id>", views.view_category, name="view_category"),
    path("bids", views.bids, name="bids"),
    path("watchlists", views.watchlists, name="watchlists"),
    path("add_to_watchlist/<int:id>", views.add_to_watchlist, name="add_to_watchlist")
]
