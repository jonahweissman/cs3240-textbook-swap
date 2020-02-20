from django.shortcuts import render
from django.views import generic
from django.contrib.auth import logout
from django.shortcuts import redirect

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
    
def Signout(request):
    logout(request)
    return redirect('/')

