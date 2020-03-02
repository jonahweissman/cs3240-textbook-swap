from django.urls import path, include
from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static


#app_name = 'marketplace'
urlpatterns = [
    path('', include('social_django.urls', namespace='social')),
    path('', views.IndexViews.as_view(), name='index'),
    path('addListing', views.ListingViews.as_view(), name = 'addListing'),
    path('myListings', views.MyListings.as_view(), name='myListings'),
    path('Signout', views.Signout, name = 'Signout'),
    path('profile', views.ProfileViews.as_view(),name = 'profile'),
    path('profile/editprofile', views.EditProfileViews.as_view(), name = 'editprofile'),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)