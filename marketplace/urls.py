from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views, email

app_name = 'marketplace'
urlpatterns = [
    path('', views.IndexViews.as_view(), name='index'),
    path('addListing', views.ListingViews.as_view(), name = 'addListing'),
    path('profile', views.ProfileViews.as_view(),name = 'profile'),
    path('search', views.SearchViews.as_view(), name='search'),
    path('myListings', views.MyListings.as_view(), name='myListings'),
    path('Signout', views.Signout, name = 'Signout'),
    path('email/send', email.send_intro_message, name='send_intro'),
    path('email/receive', email.receive_message, name='receive_message'),
    path('item/<int:pk>', views.ItemDetail.as_view(), name='item_detail'),
    path('item/<int:pk>/conversation', email.ConversationView.as_view(), name='message_list'),
    path('accounts/login/', views.login, name='login'),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
