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
    villages = models.Village.objects.all()
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
    village = get_object_or_404(models.Village, village_name=village)
    residents = models.Person.objects.filter(village=village).order_by('name')
    paginator = Paginator(residents, 75)
    residents = paginator.get_page(request.GET.get('page'))
    context = {
        'village_residents': residents,
        'paginator': residents,
        'title': 'Village overview',
        'village': village
    }

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
    village = models.Village.objects.get(person=person)
    # since date of birth is an optional field, check it's there
    if dob:
        today = datetime.date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    medical = len(models.MedicalAssessment.objects.filter(person=person))
    person.team_contact = markdown.markdown(bleach.clean(person.team_contact))
    person.family = markdown.markdown(person.family)  # already clean

    context = {
        'person': person,
        'age': age,
        'title': person.name,
        'medical': medical,
        'village': village
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
    if not models.Village.objects.all():
        msg = 'There are no villages in the database, you must add some via the admin before you can add a person.'
        try:
            errors.append(msg)
        except AttributeError:
            errors = [msg]

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


@login_required
def medical_profile(request, pk):
    template = 'people/medical_profile.html'
    person = get_object_or_404(models.Person, pk=pk)
    person.medical = markdown.markdown(bleach.clean(person.medical))
    assessments = models.MedicalAssessment.objects.filter(person=person).order_by('-date')
    for a in assessments:
        a.subjective = markdown.markdown(bleach.clean(a.subjective))
        a.objective = markdown.markdown(bleach.clean(a.objective))
        a.assessment = markdown.markdown(bleach.clean(a.assessment))
        a.plan = markdown.markdown(bleach.clean(a.plan))
        a.comment = markdown.markdown(bleach.clean(a.comment))
    context = {
        'title': '{name} medical'.format(name=person.name),
        'Person': person,
        'assessments': assessments
    }
    return render(request, template, context)


@login_required
def medical_assessment_add(request, pk):
    template = 'people/soap_new.html'
    errors = None
    person = get_object_or_404(models.Person, pk=pk)

    if request.method == 'POST':
        form = forms.SoapForm(request.POST, request.FILES)
        form.person = person
        if form.is_valid():
            try:
                form.save(person=person)
                return redirect('people:medical', pk=pk)
            except exceptions.ValidationError as e:
                errors = e

    # GET request
    if not errors:
        form = forms.SoapForm()

    context = {
        'Form': form,
        'Person': person,
        'Errors': errors,
        'title': 'New assessment'
    }
    return render(request, template, context)


@login_required
def medical_assessment_edit(request, pk, event_pk):
    template = 'people/soap_edit.html'
    person = get_object_or_404(models.Person, pk=pk)
    event = get_object_or_404(models.MedicalAssessment, pk=event_pk)
    errors = None
    # POST Request
    if request.method == 'POST':
        form = forms.SoapForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            try:
                form.save(person=person)
                return redirect('people:medical', pk=pk)
            except exceptions.ValidationError as e:
                errors = e
    # GET request
    if not errors:
        form = forms.SoapForm(instance=event)

    context = {
        'Form': form,
        'Person': person,
        'event': event,
        'Errors': errors,
        'title': 'Edit assessment'
    }
    return render(request, template, context)


@login_required
def edit_medical_notes(request, pk):
    template = 'people/medical_edit.html'
    person = get_object_or_404(models.Person, pk=pk)
    errors = None

    # POST Request
    if request.method == 'POST':
        form = forms.MedicalNotesForm(request.POST, instance=person)
        if form.is_valid():
            try:
                form.save()
                return redirect('people:medical', pk=pk)
            except exceptions.ValidationError as e:
                errors = e
    # GET request
    if not errors:
        form = forms.MedicalNotesForm(instance=person)

    context = {
        'Form': form,
        'Person': person,
        'Errors': errors,
        'title': 'Edit medical Notes'
    }
    return render(request, template, context)


@login_required
def recent_medical(request):
    template = 'people/medical_recent.html'
    assessments = models.MedicalAssessment.objects.all().order_by('-date')[:15]
    for a in assessments:
        a.subjective = markdown.markdown(bleach.clean(a.subjective))
        a.objective = markdown.markdown(bleach.clean(a.objective))
        a.assessment = markdown.markdown(bleach.clean(a.assessment))
        a.plan = markdown.markdown(bleach.clean(a.plan))
        a.comment = markdown.markdown(bleach.clean(a.comment))
    profiles = [p.person for p in assessments]
    assessments = list(zip(assessments, profiles))

    context = {
        'assessments': assessments,
        'title': 'Recent medical assessments'
    }
    return render(request, template, context)
