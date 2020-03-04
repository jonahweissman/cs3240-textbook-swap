from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth import logout
from django.utils import timezone
from django.contrib.auth.forms import UserChangeForm
from django.urls import reverse
from django.contrib.postgres.search import SearchVector, SearchQuery, TrigramDistance
from django.db.models import Q

from .forms import ImageForm
from .forms import EditProfileForm
from .models import Item, Profile

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

class ProfileViews(generic.DetailView):
    template_name = "marketplace/profilePage.html"

    def get(self, request):
        Profiles = Profile.objects.all()
        return render(request, self.template_name, {
            'user': request.user,
            'title': 'Profile'

    })


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
            return render(request, self.template_name, {
                'allItems': allItems,
            })

class SearchViews(generic.ListView):
    model = Item
    template_name = "marketplace/search_results.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(SearchViews, self).get_context_data(**kwargs)
        context['query'] = self.request.GET['query']
        page = context['page_obj']
        context['next_page'] = page.next_page_number() if page.has_next() else None
        context['previous_page'] = page.previous_page_number() if page.has_previous() else None
        return context

    def get_queryset(self):
        query = self.request.GET['query']
        field_precedence = [
            'name_distance',
            'description_distance',
            '-item_posted_date',
        ]
        hit_filter = Q(name_distance__lte=0.8) \
            | Q(description_distance__lte=0.7)
        return self.model.objects.annotate(
            name_distance=TrigramDistance('item_name', query),
            description_distance=TrigramDistance('item_description', query)
        ).filter(hit_filter).order_by(*field_precedence)

def Signout(request):
    logout(request)
    return redirect('/')
