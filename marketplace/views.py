from django.shortcuts import render
from django.views import generic
from django.utils import timezone
from django.contrib.postgres.search import SearchVector

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

class SearchViews(generic.ListView):
    model = Item
    template_name = "marketplace/search_results.html"
    context_object_name = 'search_results'
    paginate_by = 10

    def get_queryset(self):
        return self.model.objects.annotate(
            search=SearchVector('item_name', 'item_description'),
        ).filter(search=self.request.GET['query'])
