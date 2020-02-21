from django.shortcuts import render
from django.views import generic
from django.utils import timezone
from .models import Item, Profile

# Create your views here.
class IndexViews(generic.DetailView):
    template_name = "marketplace/main.html"

    def get(self, request):
        return render(request, self.template_name, {
            'user': request.user
        })


class ListingViews(generic.DetailView):
    template_name = "marketplace/addListing.html"

    def get(self, request):
        return render(request, self.template_name)


    def post(self,request):
        item_name= request.POST["item_name"]
        item_price= request.POST["item_price"]
        item_description= request.POST["item_description"]
        item_posted_date = timezone.now()
        item_condition = request.POST["item_condition"]
        item_seller_name =  Profile.objects.get(user=request.user)
        print(item_seller_name)

        item_info = Item(item_name= item_name, item_description= item_description, item_condition = item_condition, item_posted_date = item_posted_date, item_seller_name = item_seller_name, item_price= item_price)
        item_info.save()

        return render(request, self.template_name)