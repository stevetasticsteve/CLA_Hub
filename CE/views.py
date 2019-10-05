from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from CE.models import CultureEvent, TextModel, PictureModel, ParticipationModel, QuestionModel
from taggit.models import Tag
from CE.settings import culture_events_shown_on_home_page
from CE import OCM_categories

import CE.forms


def home_page(request):
    most_recent_ces = CultureEvent.objects.all().order_by(
        '-last_modified')[:culture_events_shown_on_home_page]
    context = {
        'CEs' : most_recent_ces
    }
    return render(request, 'CE/home_page.html', context)


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
    ce = get_object_or_404(CultureEvent, pk=pk)
    current_pics = PictureModel.objects.filter(ce_id=pk)

    if request.method == 'GET':
        form = CE.forms.prepopulated_CE_form(ce)
        texts = CE.forms.text_formset_prepopulated(ce)
        questions = CE.forms.question_formset_prepopulated(ce)
        participants = CE.forms.prepopulated_participants_formset(ce)


    elif request.method == 'POST':
        # CE.forms.update_CE(request, ce)
        form = CE.forms.CE_EditForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(request, instance=ce)
        # texts = CE.forms.text_form_set(request.POST, request.FILES, prefix='text')
        # questions = CE.forms.question_form_set(prefix='question')
        # if form.is_valid():
        #     form.save(request)
        return redirect('CE:view', pk=ce.pk)
    #     # todo upload multiple files at once
    #     # todo changing pictures
    #     # todo rotating pictures


    context = {
        'CE': ce,
        'TextForm': texts,
        'Form': form,
        'ParticipationForm': participants,
        'CurrentPics': current_pics,
        'QuestionForm': questions
    }
    return render(request, template, context)


@ login_required
def new(request):
    template = 'CE/new_CE.html'
    errors = None

    if request.method == 'POST':
        form = CE.forms.CE_EditForm(request.POST, request.FILES)
        text_form = CE.forms.text_form_set(request.POST, request.FILES, prefix='text')
        question_form = CE.forms.question_form_set(request.POST, prefix='question')
        participation_form = CE.forms.participant_formset(request.POST, prefix='participants')
        if form.is_valid():
            ce = form.save(request)
            for p_form in participation_form:
                if p_form.is_valid():
                    p_form.save(ce)
            for t_form in text_form:
                if t_form.is_valid():
                    t_form.save(ce)
            for question in question_form:
                if question.is_valid():
                    question.save(ce, request)
            return redirect('CE:view', pk=ce.pk)
        else:
            errors = participation_form.errors

    # GET request
    form = CE.forms.CE_EditForm()
    text_form = CE.forms.text_form_set(prefix='text')
    question_form = CE.forms.question_form_set(prefix='question')
    participation_form = CE.forms.participant_formset(prefix='participants')

    context = {
            'Form': form,
            'TextForm': text_form,
            'QuestionForm': question_form,
            'ParticipationForm': participation_form,
            'Errors': errors
        }

    return render(request, template, context)


def questions_chron(request):
    questions = QuestionModel.objects.order_by('-date_created')
    set_ces = set([i.ce for i in questions])
    context = {
        'Questions': questions,
        'CEs': set_ces
    }
    return render(request, 'CE/questions_chron.html', context)


def questions_alph(request):
    q = QuestionModel.objects.all()
    set_ces = set([i.ce for i in q])
    set_ces = sorted(set_ces, key=lambda x: x.title.lower())
    context = {
        'Questions': q,
        'CEs': set_ces
    }
    return render(request, 'CE/questions_alph.html', context)

def questions_unanswered(request):
    questions = QuestionModel.objects.filter(answer='').order_by('ce', '-last_modified')
    set_ces = set([i.ce for i in questions])
    context = {
        'Questions': questions,
        'CEs': set_ces
    }
    return render(request, 'CE/questions_unanswered.html', context)


def questions_recent(request):
    questions = QuestionModel.objects.all().exclude(answer='').order_by('ce', '-last_modified')
    set_ces = set([i.ce for i in questions])
    context = {
        'Questions': questions,
        'CEs': set_ces
    }
    return render(request, 'CE/questions_recent.html', context)


def OCM_home(request):
    template = 'CE/OCM_home.html'
    context = {
        'OCM': OCM_categories.OCM,
        'Sections': OCM_categories.OCM_categories
    }
    return render(request, template, context)


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

def tag_list_page(request):
    template = 'CE/tag_list_page.html'
    tags = Tag.objects.all().annotate(num=Count('taggit_taggeditem_items')).order_by('-num')
    context = {
        'Tags': tags
    }
    return render(request, template, context)

