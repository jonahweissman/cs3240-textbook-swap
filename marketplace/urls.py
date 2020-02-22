from django.urls import path, include
from . import views

#app_name = 'marketplace'
urlpatterns = [
    path('', include('social_django.urls', namespace='social')),
    path('', views.IndexViews.as_view(), name='index'),
    path('addListing', views.ListingViews.as_view(), name = 'addListing'),
    path('myListings', views.MyListings.as_view(), name='myListings'),
    path('Signout', views.Signout, name = 'Signout'),
]