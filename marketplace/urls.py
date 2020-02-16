from django.urls import path, include

from . import views

#app_name = 'marketplace'
urlpatterns = [
    path('', include('social_django.urls', namespace='social')),
    path('', views.IndexViews.as_view(), name='index'),
    path('addListing', views.ListingViews.as_view(), name = 'addListing'),
]
