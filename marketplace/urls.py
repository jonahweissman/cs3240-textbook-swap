from django.urls import path, include
from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name = 'marketplace'
urlpatterns = [
    path('', views.IndexViews.as_view(), name='index'),
    path('addListing', views.ListingViews.as_view(), name = 'addListing'),
    path('profile', views.ProfileViews.as_view(),name = 'profile'),
    path('profile/editprofile', views.EditProfileViews.as_view(), name = 'editprofile'),
    path('search', views.SearchViews.as_view(), name='search'),
    path('myListings', views.MyListings.as_view(), name='myListings'),
    path('Signout', views.Signout, name = 'Signout'),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)