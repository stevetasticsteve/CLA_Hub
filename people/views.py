from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from people import forms

@login_required
def people_home(request):
    template = 'people/home.html'
    context = {

    }
    return render(request, template, context)


@login_required
def alphabetically(request):
    template = 'people/alphabetical.html'
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

@login_required
def new(request):
    template = 'people/new.html'
    form = forms.PeopleForm()
    context = {
        'Form': form
    }
    return render(request, template, context)