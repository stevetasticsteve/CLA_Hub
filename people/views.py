from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core import exceptions

import datetime

from people import forms
from people import models


@login_required
def people_home(request):
    template = 'people/home.html'

    context = {

    }
    return render(request, template, context)

@login_required
def village(request, village):
    template = 'people/village.html'
    residents = models.Person.objects.filter(village=village)
    context = {
        'village_residents': residents,
    }
    # pull the villages display name from the model and 404 if out of range
    try:
        context['village'] = models.Person.villages[village - 1][1]
    except IndexError:
        return render(request, '404.html')
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
    person = get_object_or_404(models.Person, pk=pk)
    age = None
    dob = person.born
    # since date of birth is an optional field, check it's there
    if dob:
        today = datetime.date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    context = {
        'person': person,
        'age': age
    }
    return render(request, template, context)


@login_required
def new(request):
    template = 'people/new.html'
    errors = None

    if request.method == 'POST':
        form = forms.PeopleForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                person = form.save(request=request)
                return redirect('people:detail', pk=person.pk)
            except exceptions.ValidationError as e:
                errors = e

    # GET request
    if not errors:  # don't overwrite the user's failed form
        form = forms.PeopleForm()

    context = {
        'Form': form,
        'Errors': errors
    }
    return render(request, template, context)