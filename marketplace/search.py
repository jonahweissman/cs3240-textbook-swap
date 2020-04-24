from django.views import generic
from django.contrib.postgres.search import SearchVector, SearchQuery, TrigramBase
from django.db.models import Q

from . import models

class TrigramWordDistance(TrigramBase):
    function = ''
    arg_joiner = ' <->> '

class SearchViews(generic.ListView):
    model = models.Item
    template_name = "marketplace/search_results.html"
    paginate_by = 10
    sort_mapping = {
        'relevance': [
            'name_distance',
            'author_distance',
            'course_distance',
            'description_distance',
        ],
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
        hit_filter = (Q(name_distance__lte=0.8) \
                     | Q(description_distance__lte=0.7) \
                     | Q(author_distance__lte=0.7) \
                     | Q(course_distance__lte=0.3) \
                     | Q(item_isbn=query)) \
                     & Q(item_status='Available')
        return self.model.objects.annotate(
            name_distance=TrigramWordDistance('item_name', query),
            description_distance=TrigramWordDistance('item_description', query),
            course_distance=TrigramWordDistance('item_course', query),
            author_distance=TrigramWordDistance('item_author', query),
        ).filter(hit_filter).order_by(*order_by)
