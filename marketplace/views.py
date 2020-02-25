from django.shortcuts import render
from django.views import generic
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from .models import Profile
from .forms import ImageForm

# Create your views here.
class IndexViews(generic.DetailView):
    template_name = "marketplace/main.html"

    def get(self, request):
        return render(request, self.template_name, {
            'user': request.user
        })


class ListingViews(generic.DetailView):
    template_name = "marketplace/createNewListing.html"

    def get(self, request):
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
    def post(self, request):
        form = ImageForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
        else: 
            form = ImageForm()
        args = {"form" : form}
        return render(request, self.template_name, args)
    
def Signout(request):
    logout(request)
    return redirect('/')

class EditProfileViews(generic.DetailView):
    template_name = "marketplace/edit_profile.html"

    def get(self, request):
        return render(request, self.template_name, {
            'user': request.user
    })
