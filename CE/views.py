import bleach
import markdown
from django import forms
from django.contrib.auth.decorators import login_required
from django.core import exceptions
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import Lower
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaulttags import register
from taggit.models import Tag

import CE.forms
import CE.utilities
from CE import OCM_categories
from CE.models import CultureEvent, Text, Picture, Visit, Question

text_form_factory = forms.inlineformset_factory(CE.models.CultureEvent, CE.models.Text,
                                                form=CE.forms.TextForm, extra=0)

question_form_factory = forms.inlineformset_factory(CE.models.CultureEvent, CE.models.Question,
                                                    form=CE.forms.QuestionForm, extra=0)

visits_form_factory = forms.inlineformset_factory(CE.models.CultureEvent, CE.models.Visit,
                                                  form=CE.forms.VisitsForm, extra=0)


@CE.utilities.conditional_login
def home_page(request):
    most_recent_ces = CultureEvent.objects.all().order_by('-last_modified')
    paginator = Paginator(most_recent_ces, 25)
    CEs = paginator.get_page(request.GET.get('page'))
    context = {
        'CEs': CEs,
        'paginator': CEs,
        'title': 'CE home',
        'search_context': 'CE'
    }
    return render(request, 'CE/home_page.html', context)


@CE.utilities.conditional_login
def alphabetical(request):
    ces = CultureEvent.objects.all().order_by(Lower('title'))
    paginator = Paginator(ces, 25)
    ces = paginator.get_page(request.GET.get('page'))
    context = {
        'CEs': ces,
        'paginator': ces,
        'title': 'CEs alphabetically'
    }
    return render(request, 'CE/alphabetical.html', context)


@CE.utilities.conditional_login
def view(request, pk):
    ce = get_object_or_404(CultureEvent, pk=pk)
    texts = Text.objects.filter(ce=pk)
    pictures = Picture.objects.filter(ce=pk)
    visits = Visit.objects.filter(ce=ce)
    questions = Question.objects.filter(ce=ce)
    tags = ce.tags.all()

    ce.description = markdown.markdown(ce.description)  # don't need to clean it since model handles that
    ce.interpretation = markdown.markdown(bleach.clean(ce.interpretation))
    ce.differences = markdown.markdown(bleach.clean(ce.differences))

    context = {
        'CE': ce,
        'Texts': texts,
        'Pics': pictures,
        'Visits': visits,
        'Questions': questions,
        'Tags': tags,
        'title': ce.title
    }
    return render(request, 'CE/view_CE.html', context)


@CE.utilities.conditional_login
def view_slug(request, slug):
    ce = get_object_or_404(CultureEvent, slug=slug)
    return view(request, ce.pk)


@login_required
def edit(request, pk):
    template = 'CE/edit_CE.html'
    errors = None

    ce = get_object_or_404(CultureEvent, pk=pk)
    text_form = text_form_factory(prefix='text', instance=ce)
    question_form = question_form_factory(prefix='question', instance=ce)
    visit_form = visits_form_factory(prefix='visit', instance=ce)
    current_pics = Picture.objects.filter(ce_id=pk)

    if request.method == 'POST':
        form = CE.forms.CE_EditForm(request.POST, request.FILES)
        text_form = text_form_factory(request.POST, request.FILES, prefix='text', instance=ce)
        question_form = question_form_factory(request.POST, request.FILES, prefix='question', instance=ce)
        visit_form = visits_form_factory(request.POST, prefix='visit', instance=ce)
        if form.is_valid():
            try:
                form.save(request, instance=ce)
                # required to loop through formsets when passing kwargs
                for text in text_form:
                    if text_form.is_valid():
                        text.save(request=request)
                for visit in visit_form:
                    if visit.is_valid():
                        visit.save()
                for question in question_form:
                    if question.is_valid():
                        question.save(request=request)
                return redirect('CE:view', pk=ce.pk)
            except exceptions.ValidationError as e:
                errors = e

    if not errors:  # don't overwrite the user's failed form
        form = CE.forms.prepopulated_CE_form(ce)

    context = {
        'TextForm': text_form,
        'Form': form,
        'VisitForm': visit_form,
        'CurrentPics': current_pics,
        'QuestionForm': question_form,
        'Errors': errors,
        'CE': ce,
        'button_text': 'Update CE',
        'title': 'Edit ' + str(ce.title)
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
    visit_form = visits_form_factory(prefix='visit', instance=None)

    if request.method == 'POST':
        form = CE.forms.CE_EditForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                ce = form.save(request)
                text_form = text_form_factory(request.POST, request.FILES, prefix='text', instance=ce)
                question_form = question_form_factory(request.POST, prefix='question', instance=ce)
                visit_form = visits_form_factory(request.POST, prefix='visit', instance=ce)

                if visit_form.is_valid():
                    visit_form.save()
                    # required to loop through formsets when passing kwargs
                    for text in text_form:
                        if text_form.is_valid():
                            text.save(request=request)
                for question in question_form:
                    if question.is_valid():
                        question.save(request=request)

                # success, send user to new CE
                return redirect('CE:view', pk=ce.pk)
            except exceptions.ValidationError as e:
                # return a validation error in event of valid form,
                # but CE already existing, show form to user again
                errors = e  # todo any user added text info will disappear on form resubmission

        else:
            # return form for user to try again showing incorrect fields
            errors = form.errors

    # GET request
    if not errors:  # don't overwrite the user's failed form
        form = CE.forms.CE_EditForm()

    context = {
        'Form': form,
        'TextForm': text_form,
        'QuestionForm': question_form,
        'VisitForm': visit_form,
        'Errors': errors,
        'button_text': 'Create CE',
        'title': 'new_CE'
    }

    return render(request, template, context)


@CE.utilities.conditional_login
def questions_chron(request):
    questions = Question.objects.order_by('-date_created')
    set_ces = set([i.ce for i in questions])
    paginator = Paginator(questions, 25)
    questions = paginator.get_page(request.GET.get('page'))
    context = {
        'Questions': questions,
        'paginator': questions,
        'CEs': set_ces
    }
    return render(request, 'CE/questions_chron.html', context)


@CE.utilities.conditional_login
def questions_alph(request):
    q = Question.objects.all()
    paginator = Paginator(q, 25)
    q = paginator.get_page(request.GET.get('page'))
    set_ces = set([i.ce for i in q])
    set_ces = sorted(set_ces, key=lambda x: x.title.lower())
    context = {
        'Questions': q,
        'paginator': q,
        'CEs': set_ces,
        'title': 'Questions'
    }
    return render(request, 'CE/questions_alph.html', context)


@CE.utilities.conditional_login
def questions_unanswered(request):
    questions = Question.objects.filter(answer='').order_by('ce', '-last_modified')
    paginator = Paginator(questions, 25)
    questions = paginator.get_page(request.GET.get('page'))
    set_ces = set([i.ce for i in questions])
    context = {
        'Questions': questions,
        'paginator': questions,
        'CEs': set_ces,
        'title': 'Questions'
    }
    return render(request, 'CE/questions_unanswered.html', context)


@CE.utilities.conditional_login
def questions_recent(request):
    questions = Question.objects.all().exclude(answer='').order_by('ce', '-last_modified')
    paginator = Paginator(questions, 25)
    questions = paginator.get_page(request.GET.get('page'))
    set_ces = set([i.ce for i in questions])
    context = {
        'Questions': questions,
        'paginator': questions,
        'CEs': set_ces,
        'title': 'Questions'
    }
    return render(request, 'CE/questions_recent.html', context)


@CE.utilities.conditional_login
def OCM_home(request):
    template = 'CE/OCM_home.html'
    # pull up all tags from .db with their frequency
    tags = Tag.objects.all().annotate(num=Count('taggit_taggeditem_items'))
    # filter it down to just OCM tags
    tagged_OCM = {tag.name: tag.num for tag in tags if tag.name in OCM_categories.categories}

    context = {
        'OCM': OCM_categories.OCM,
        'Sections': OCM_categories.OCM_categories,
        'Tags': tagged_OCM,
        'title': 'OCM tags'
    }
    return render(request, template, context)


@CE.utilities.conditional_login
def OCM_ref(request):
    template = 'CE/OCM_ref.html'
    context = {
        'OCM': OCM_categories.OCM,
        'Sections': OCM_categories.OCM_categories,
        'title': 'OCM reference'
    }
    return render(request, template, context)


@register.filter
# a filter so that templates can use something in it's loop
# as a lookup in a dictionary
def get_item(dictionary, key):
    return dictionary.get(key)


@CE.utilities.conditional_login
def tag_detail_page(request, slug):
    template = 'CE/tag_detail_page.html'
    tag = get_object_or_404(Tag, slug=slug)
    # filter CEs by tag name
    CEs = CultureEvent.objects.filter(tags=tag)

    context = {
        'tag': tag,
        'CEs': CEs,
        'title': tag
    }

    return render(request, template, context)


@CE.utilities.conditional_login
def tag_list_page(request):
    template = 'CE/all_tags.html'
    tags = Tag.objects.all().annotate(num=Count('taggit_taggeditem_items')).order_by('-num')
    context = {
        'Tags': tags,
        'title': 'Tags',
        'search_context': 'tags'
    }
    return render(request, template, context)


@CE.utilities.conditional_login
def tags_search(request):
    template = 'search_results.html'
    search = request.GET.get('search')
    results = Tag.objects.filter(Q(name__icontains=search))
    context = {
        'search': search,
        'Tags': results,
        'title': 'CE search',
        'search_context': 'tags'
    }
    return render(request, template, context)


@CE.utilities.conditional_login
def search_CE(request):
    template = 'search_results.html'
    search = request.GET.get('search')
    results = CultureEvent.objects.filter(Q(title__icontains=search))
    context = {
        'search': search,
        'CEs': results,
        'title': 'CE search',
        'search_context': 'CE'
    }
    return render(request, template, context)


@CE.utilities.conditional_login
def texts_home(request):
    template = 'CE/texts.html'
    texts = Text.objects.all().order_by('-last_modified')
    context = {
        'Texts': texts,
        'title': 'Texts',
        'search_context': 'texts'
    }
    return render(request, template, context)


@CE.utilities.conditional_login
def text_genre(request, genre):
    template = 'CE/texts_genre.html'
    texts = Text.objects.filter(discourse_type=genre).order_by('-last_modified')
    # Find the genre that goes to the number
    # if out of range return 404
    if int(genre) <= len(Text.genres):
        genre = Text.genres[int(genre) - 1][1]
    else:
        return render(request, '404.html')

    context = {
        'Texts': texts,
        'Genre': genre,
        'title': genre + ' texts'
    }
    return render(request, template, context)


@CE.utilities.conditional_login
def text_search(request):
    template = 'search_results.html'
    search = request.GET.get('search')
    results = Text.objects.filter(Q(text_title__icontains=search))
    context = {
        'search': search,
        'Texts': results,
        'title': 'Text search',
        'search_context': 'texts'
    }
    return render(request, template, context)
