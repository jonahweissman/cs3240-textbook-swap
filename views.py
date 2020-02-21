from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.forms import UserChangeForm
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
        return render(request, self.template_name, {
            'user': request.user
        })

def editProfileView(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST,instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('/profile')
    else:
        form = UserChangeForm(instance=request.user)
        args = {'form': form}
        return render(request, 'marketplace/edit_profile.html', args)

def Signout(request):
    logout(request)
    return redirect('/')

