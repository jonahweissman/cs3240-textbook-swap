from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static 
from . import views

#app_name = 'marketplace'
urlpatterns = [
    path('', include('social_django.urls', namespace='social')),
    path('', views.IndexViews.as_view(), name='index'),
    path('addListing', views.ListingViews.as_view(), name = 'addListing'),
    path('profile', views.ProfileViews.as_view(), name = 'profile'),
    path('profile/editprofile', views.EditProfileViews.as_view(), name = 'editprofile'),
    path('Signout', views.Signout, name = 'Signout'),
]

if settings.DEBUG: 
        urlpatterns += static(settings.MEDIA_URL, 
                              document_root=settings.MEDIA_ROOT) 