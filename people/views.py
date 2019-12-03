from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def people_home(request):
    template = 'people/home.html'
    context = {

    }
    return render(request, template, context)

@login_required
def people_detail(request, pk):
    template = 'people/detail.html'
    context = {
        'person': pk
    }
    return render(request, template, context)