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
from django.shortcuts import get_object_or_404
from django.contrib import messages
import requests

from .forms import ImageForm, ItemForm
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
            item_condition = request.POST.get("item_condition", "defaultCondition")
            item_seller_name =  Profile.objects.get(user=request.user)

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

            if item_description == "No description entered" and item_isbn != "defaultName":
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
                item.save()
                messages.success(request, 'Your form was submitted successfully!')
            else:
                messages.success(request, 'ERROR! Your form could not be submitted.')

            return render(request, self.template_name, args)

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
            return render(request, self.template_name, {
                'allItems': allItems,
            })

class SearchViews(generic.ListView):
    model = Item
    template_name = "marketplace/search_results.html"
    paginate_by = 10
    sort_mapping = {
        'relevance': ['name_distance',
                      'author_distance',
                      'description_distance',
                      'isbn_distance'],
        'date': ['-item_posted_date'],
        'price': ['item_price'],
    }
    sort_default = 'relevance'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET['query']
        context['sort'] = self.request.GET.get('sort', self.sort_default)
        page = context['page_obj']
        context['next_page'] = page.next_page_number() if page.has_next() else None
        context['previous_page'] = page.previous_page_number() if page.has_previous() else None
        context['sort_options'] = self.sort_mapping.keys()
        return context

    def get_queryset(self):
        query = self.request.GET['query']
        sort_by = self.request.GET.get('sort', self.sort_default)
        order_by = self.sort_mapping[sort_by]
        hit_filter = Q(name_distance__lte=0.8) \
            | Q(description_distance__lte=0.7) \
            | Q(isbn_distance__lte=0.5) \
            | Q(author_distance__lte=0.7)
        return self.model.objects.annotate(
            name_distance=TrigramDistance('item_name', query),
            description_distance=TrigramDistance('item_description', query),
            isbn_distance=TrigramDistance('item_isbn', query),
            author_distance=TrigramDistance('item_author', query),
        ).filter(hit_filter).order_by(*order_by)


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
