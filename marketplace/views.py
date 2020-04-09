from django.shortcuts import render
from django.views import generic
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.forms import UserChangeForm
from django.urls import reverse
from .forms import ImageForm
from .forms import EditProfileForm
from django.db.models import Q
from .models import Item, Profile
from django.shortcuts import get_object_or_404


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
    context_object_name = 'search_results'
    paginate_by = 10
    sort_mapping = {
        'date': '-item_posted_date',
        'price': 'item_price',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET['query']
        context['sort'] = self.request.GET.get('sort', 'date')
        page = context['page_obj']
        context['next_page'] = page.next_page_number() if page.has_next() else None
        context['previous_page'] = page.previous_page_number() if page.has_previous() else None
        context['sort_options'] = self.sort_mapping.keys()
        return context

    def get_queryset(self):
        query = self.request.GET['query']
        sort_by = self.request.GET.get('sort', 'date')
        order_by = self.sort_mapping[sort_by]
        return self.model.objects.all().filter(
            Q(item_name__icontains=query)
            | Q(item_description__icontains=query)
        ).order_by(order_by)

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
