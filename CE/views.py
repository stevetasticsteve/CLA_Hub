from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core import exceptions
from CE.models import CultureEvent, TextModel, PictureModel, ParticipationModel, QuestionModel
from taggit.models import Tag
from CE.settings import culture_events_shown_on_home_page
from CE import OCM_categories
from django import forms

import CE.forms
import CE.utilities

text_form_factory = forms.inlineformset_factory(CE.models.CultureEvent, CE.models.TextModel,
                                                form=CE.forms.TextForm, extra=0)

question_form_factory = forms.inlineformset_factory(CE.models.CultureEvent, CE.models.QuestionModel,
                                                    form=CE.forms.QuestionForm, extra=0)

participation_form_factory = forms.inlineformset_factory(CE.models.CultureEvent, CE.models.ParticipationModel,
                                                         form=CE.forms.ParticipationForm, extra=1)


@CE.utilities.conditional_login
def home_page(request):
    most_recent_ces = CultureEvent.objects.all().order_by(
        '-last_modified')[:culture_events_shown_on_home_page]
    context = {
        'CEs' : most_recent_ces
    }
    return render(request, 'CE/home_page.html', context)


@CE.utilities.conditional_login
def view(request, pk):
    ce = get_object_or_404(CultureEvent, pk=pk)
    texts = TextModel.objects.filter(ce=pk)
    pictures = PictureModel.objects.filter(ce=pk)
    participants = ParticipationModel.objects.filter(ce=ce)
    questions = QuestionModel.objects.filter(ce=ce)
    tags = ce.tags.all()
    context = {
        'CE' : ce,
        'Texts' : texts,
        'Pics' : pictures,
        'Participants' : participants,
        'Questions': questions,
        'Tags': tags,
    }
    return render(request, 'CE/view_CE.html', context)


@CE.utilities.conditional_login
def view_slug(request, slug):
    ce = get_object_or_404(CultureEvent, slug=slug)
    pk = ce.pk
    texts = TextModel.objects.filter(ce=pk)
    pictures = PictureModel.objects.filter(ce=pk)
    participants = ParticipationModel.objects.filter(ce=ce)
    context = {
        'CE' : ce,
        'Texts' : texts,
        'Pics' : pictures,
        'Participants' : participants
    }
    return render(request, 'CE/view_CE.html', context)


@login_required
def edit(request, pk):
    template = 'CE/edit_CE.html'
    errors = None

    ce = get_object_or_404(CultureEvent, pk=pk)
    text_form = text_form_factory(prefix='text', instance=ce)
    question_form = question_form_factory(prefix='question', instance=ce)
    participants_form = participation_form_factory(prefix='participants', instance=ce)
    current_pics = PictureModel.objects.filter(ce_id=pk)

    if request.method == 'POST':
        form = CE.forms.CE_EditForm(request.POST, request.FILES)
        questions = CE.forms.question_formset_prepopulated(ce)
        text_form = text_form_factory(request.POST, request.FILES, prefix='text', instance=ce)
        if form.is_valid():
            try:
                form.save(request, instance=ce)
                for t_form in text_form:
                    if t_form.is_valid():
                        t_form.save()
                return redirect('CE:view', pk=ce.pk)
            except exceptions.ValidationError as e:
                errors = e

        # texts = CE.forms.text_form_set(request.POST, request.FILES, prefix='text')
        # questions = CE.forms.question_form_set(prefix='question')
        # if form.is_valid():
        #     form.save(request)

    if not errors:  # don't overwrite the user's failed form
        form = CE.forms.prepopulated_CE_form(ce)

    context = {
        'TextForm': text_form,
        'Form': form,
        'ParticipationForm': participants_form,
        'CurrentPics': current_pics,
        'QuestionForm': questions,
        'Errors': errors
    }
    return render(request, template, context)
# todo upload multiple files at once
# todo changing pictures
# todo rotating pictures


@login_required
def new(request):
    template = 'CE/new_CE.html'
    errors = None
    text_form = text_form_factory(prefix='text', instance=None)
    question_form = question_form_factory(prefix='question', instance=None)
    participation_form = participation_form_factory(prefix='participants', instance=None)

    if request.method == 'POST':
        form = CE.forms.CE_EditForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                ce = form.save(request)
                text_form = text_form_factory(request.POST, request.FILES, prefix='text', instance=ce)
                question_form = question_form_factory(request.POST, prefix='question', instance=ce)
                participation_form = participation_form_factory(request.POST, prefix='participants', instance=ce)

                if participation_form.is_valid():
                    participation_form.save()
                if text_form.is_valid():
                    text_form.save()
                for question in question_form:
                    if question.is_valid():
                        question.save(request=request)

                # success, send user to new CE
                return redirect('CE:view', pk=ce.pk)
            except exceptions.ValidationError as e:
                # return a validation error in event of valid form,
                # but CE already existing, show form to user again
                errors = e
        else:
            # return form for user to try again showing incorrect fields
            errors = form.errors

    # GET request
    if not errors: # don't overwrite the user's failed form
        form = CE.forms.CE_EditForm()

    context = {
            'Form': form,
            'TextForm': text_form,
            'QuestionForm': question_form,
            'ParticipationForm': participation_form,
            'Errors': errors
        }

    return render(request, template, context)


@CE.utilities.conditional_login
def questions_chron(request):
    questions = QuestionModel.objects.order_by('-date_created')
    set_ces = set([i.ce for i in questions])
    context = {
        'Questions': questions,
        'CEs': set_ces
    }
    return render(request, 'CE/questions_chron.html', context)


@CE.utilities.conditional_login
def questions_alph(request):
    q = QuestionModel.objects.all()
    set_ces = set([i.ce for i in q])
    set_ces = sorted(set_ces, key=lambda x: x.title.lower())
    context = {
        'Questions': q,
        'CEs': set_ces
    }
    return render(request, 'CE/questions_alph.html', context)


@CE.utilities.conditional_login
def questions_unanswered(request):
    questions = QuestionModel.objects.filter(answer='').order_by('ce', '-last_modified')
    set_ces = set([i.ce for i in questions])
    context = {
        'Questions': questions,
        'CEs': set_ces
    }
    return render(request, 'CE/questions_unanswered.html', context)


@CE.utilities.conditional_login
def questions_recent(request):
    questions = QuestionModel.objects.all().exclude(answer='').order_by('ce', '-last_modified')
    set_ces = set([i.ce for i in questions])
    context = {
        'Questions': questions,
        'CEs': set_ces
    }
    return render(request, 'CE/questions_recent.html', context)


@CE.utilities.conditional_login
def OCM_home(request):
    template = 'CE/OCM_home.html'
    context = {
        'OCM': OCM_categories.OCM,
        'Sections': OCM_categories.OCM_categories
    }
    return render(request, template, context)


@CE.utilities.conditional_login
def tag_detail_page(request, slug):
    template = 'CE/tag_detail_page.html'
    tag = get_object_or_404(Tag, slug=slug)
    # filter CEs by tag name
    CEs = CultureEvent.objects.filter(tags=tag)

    context = {
        'tag':tag,
        'CEs':CEs,
    }

    return render(request, template, context)


@CE.utilities.conditional_login
def tag_list_page(request):
    template = 'CE/tag_list_page.html'
    tags = Tag.objects.all().annotate(num=Count('taggit_taggeditem_items')).order_by('-num')
    context = {
        'Tags': tags
    }
    return render(request, template, context)

