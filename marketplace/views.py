from django.shortcuts import render
from django.views import generic
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.forms import UserChangeForm
from django.urls import reverse
from .forms import ImageForm, ItemForm
from .forms import EditProfileForm
from .models import Item, Profile
from django.shortcuts import get_object_or_404
from django.contrib import messages

import requests



# Create your views here.
class IndexViews(generic.ListView):
    template_name = "marketplace/main.html"
    context_object_name = "allItems"
    num_listings_display = 30

    def get_queryset(self):
        return Item.objects.filter(item_status="Available") \
            .order_by('-item_posted_date')[:self.num_listings_display]

class ListingViews(generic.DetailView):
    template_name = "marketplace/addListing.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, self.template_name, {
                'error_message': 'Must be Logged In',
            })
        else:
            form1 = ItemForm()
            args = {'form1': form1}
            return render(request, self.template_name, args)

    def post(self,request):
            item_name= request.POST.get("item_name", "defaultName")
            item_isbn= request.POST.get("item_isbn", "defaultName")
            #remove '-' if it contains
            item_isbn = item_isbn.replace('-', '')
            item_edition= request.POST.get("item_edition", -1)
            item_author= request.POST.get("item_author", "defaultAuthor")
            item_course= request.POST.get("item_course", "defaultCourse")
            item_price= request.POST.get("item_price", -1 )
            item_description= request.POST.get("item_description", "No description entered")
            item_posted_date = timezone.now()
            item_condition = request.POST.get("item_condition", "Like New")
            item_seller_name =  Profile.objects.get(user=request.user)
            item_status = request.POST.get("item_status", "Available")

            form1 = ItemForm(request.POST, request.FILES)
            args = {"form1": form1}

             #check if author and title has been set, if not fill using information returned by API
            info_from_api = requests.get('https://www.googleapis.com/books/v1/volumes?q=isbn:'+ item_isbn).json()
            
            if item_name == "defaultName":
                try:
                    item_name= info_from_api['items'][0]['volumeInfo']['title']
                except:
                    messages.error(request, 'ISBN not found! Please submit using Title/Author')
                    return render(request, self.template_name,args)

            if item_author == "defaultAuthor":
                item_author = info_from_api['items'][0]['volumeInfo']['authors'][0]

            if item_description == "" and item_isbn != "defaultName":
                item_description= info_from_api['items'][0]['volumeInfo']['description']

            
            if form1.is_valid():
                item = form1.save(commit = "false")
                item.item_isbn = item_isbn
                item.item_name = item_name
                item.item_edition = item_edition
                item.item_author = item_author
                item.item_course= item_course
                item.item_price= item_price
                item.item_description = item_description
                item.item_posted_date = item_posted_date
                item.item_condition = item_condition 
                item.item_seller_name = item_seller_name
                item.item_status = item_status
                item.save()
                messages.success(request, 'Your form was submitted successfully!')
            else:
                messages.error(request, 'ERROR! Your form could not be submitted.')

            return render(request, self.template_name, args)


class UpdateListingView(generic.UpdateView):
    model = Item
    template_name = 'marketplace/update_listing.html'
    fields = ['item_status']


class ProfileViews(generic.DetailView):
    template_name = "marketplace/profilePage.html"

    def get(self, request):
        Profiles = Profile.objects.all()
        form = ImageForm()
        return render(request, self.template_name, {
            'user': request.user, "form": form
    })

    def post(self, request):
        form = ImageForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
        else:
            form = ImageForm()
        args = {"form": form}
        return render(request, self.template_name, args)


class MyListings(generic.ListView):
    template_name = "marketplace/myListings.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, self.template_name, {
                'error_message': 'Must be Logged In',
            })
        else:
            user = get_object_or_404(Profile, user=request.user)
            allItems = Item.objects.filter(item_seller_name=user)
            availableItems = Item.objects.filter(item_status="Available",item_seller_name=user )
            soldItems = Item.objects.filter(item_status="Sold", item_seller_name=user)
            hiddenItems = Item.objects.filter(item_status="Hidden", item_seller_name=user)
            return render(request, self.template_name, {
                'allItems': allItems,
                'availableItems': availableItems,
                'soldItems': soldItems,
                'hiddenItems': hiddenItems,
            })


class ItemDetail(generic.DetailView):
    model=Item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_has_buyer_conversation'] = context['object'].conversation_set.all().filter(buyer=self.request.user.profile).exists()
        return context


def Signout(request):
    logout(request)
    return redirect('/')

def login(request):
    login_page = reverse('social:begin', args=['google-oauth2'])
    if 'next' in request.GET:
        login_page += '?next=' + request.GET['next']
    return redirect(login_page)
