import datetime

import bleach
import markdown
from django.contrib.auth.decorators import login_required
from django.core import exceptions
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from people import forms
from people import models


@login_required
def people_home(request):
    template = 'people/home.html'
    recently_edited = models.Person.objects.all().order_by(
        '-last_modified')[:24]
    villages = dict(models.Person.villages)
    context = {
        'profiles': recently_edited,
        'villages': villages,
        'title': 'CLAHub People',
        'search_context': 'people',
    }
    return render(request, template, context)


@login_required
def village(request, village):
    template = 'people/village.html'
    residents = models.Person.objects.filter(village=village).order_by('name')
    paginator = Paginator(residents, 25)
    residents = paginator.get_page(request.GET.get('page'))
    context = {
        'village_residents': residents,
        'paginator': residents,
        'title': 'Village overview'
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
    people = models.Person.objects.all().order_by(
        'name')
    paginator = Paginator(people, 25)
    people = paginator.get_page(request.GET.get('page'))
    context = {
        'People': people,
        'paginator': people,
        'title': 'People alphabetically'
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

    person.team_contact = markdown.markdown(bleach.clean(person.team_contact))
    person.family = markdown.markdown(person.family)  # already clean

    context = {
        'person': person,
        'age': age,
        'title': person.name
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
        'Errors': errors,
        'title': 'New person'
    }
    return render(request, template, context)


@login_required
def edit(request, pk):
    template = 'people/edit.html'
    person = get_object_or_404(models.Person, pk=pk)
    errors = None

    if request.method == 'POST':
        form = forms.PeopleForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            try:
                form.save(request=request)
                return redirect('people:detail', pk=pk)
            except exceptions.ValidationError as e:
                errors = e

    if not errors:
        form = forms.PeopleForm(instance=person)

    context = {
        'Form': form,
        'Errors': errors,
        'title': 'Edit ' + person.name
    }
    return render(request, template, context)


def help_family(request):
    return render(request, 'people/help/family_help.html')


@login_required
def search_people(request):
    template = 'search_results.html'
    search = request.GET.get('search')
    results = models.Person.objects.filter(Q(name__icontains=search)).order_by('name')
    paginator = Paginator(results, 25)
    results = paginator.get_page(request.GET.get('page'))
    context = {
        'search': search,
        'profiles': results,
        'paginator': results,
        'title': 'People search',
        'search_context': 'people'
    }
    return render(request, template, context)
