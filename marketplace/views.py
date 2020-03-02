from django.shortcuts import render
from django.views import generic
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
from .models import Item, Profile
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserChangeForm
from django.urls import reverse
from .forms import ImageForm
from .forms import EditProfileForm

# Create your views here.
class IndexViews(generic.ListView):
    template_name = "marketplace/main.html"
    context_object_name = "allItems"

    def get_queryset(self):
        return Item.objects.all()

class ListingViews(generic.DetailView):
    template_name = "marketplace/addListing.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, self.template_name, {
                'error_message': 'Must be Logged In',
            })
        else:
            return render(request, self.template_name)

    def post(self,request):
            item_name= request.POST["item_name"]
            item_price= request.POST["item_price"]
            item_description= request.POST["item_description"]
            item_posted_date = timezone.now()
            item_condition = request.POST["item_condition"]
            item_seller_name =  Profile.objects.get(user=request.user)

            item_info = Item(item_name= item_name, item_description= item_description, item_condition = item_condition, item_posted_date = item_posted_date, item_seller_name = item_seller_name, item_price= item_price)
            item_info.save()

            return render(request, self.template_name)


class MyListings(generic.ListView):
    template_name = "marketplace/myListings.html"
    #context_object_name = 'allItems'

    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, self.template_name, {
                'error_message': 'Must be Logged In',
            })
        else:
            user = get_object_or_404(Profile, user=request.user)
            allItems = Item.objects.filter(item_seller_name=user)
            return render(request, self.template_name, {
                'allItems': allItems,
            })

class ProfileViews(generic.DetailView):
    template_name = "marketplace/profilePage.html"

    def get(self, request):
        # Profiles = Profile.objects.all()
        return render(request, self.template_name, {
            'user': request.user
        })

class ProfileViews(generic.DetailView):
    template_name = "marketplace/profilePage.html"

    def get(self, request):
        Profiles = Profile.objects.all()
        return render(request, self.template_name, {
            'user': request.user

    })

def Signout(request):
    logout(request)
    return redirect('/')

class EditProfileViews(generic.DetailView):
    template_name = "marketplace/edit_profile.html"

    def get(self, request):
        return render(request, self.template_name, {
            'user': request.user
    })

    def post(self, request):
        form = ImageForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
        else:
            form = ImageForm()
        args = {"form": form}
        return render(request, self.template_name, args)