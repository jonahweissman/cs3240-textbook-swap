from django.shortcuts import render

# Create your views here.
def index(request):
    context = {
        'name': request.user.first_name
    }
    return render(request, 'marketplace/main.html', context)
