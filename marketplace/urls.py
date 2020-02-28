from django.urls import path, include
from . import views

app_name = 'marketplace'
urlpatterns = [
    path('', views.IndexViews.as_view(), name='index'),
    path('addListing', views.ListingViews.as_view(), name = 'addListing'),
    path('search', views.SearchViews.as_view(), name='search'),
    path('myListings', views.MyListings.as_view(), name='myListings'),
    path('Signout', views.Signout, name = 'Signout'),
]
