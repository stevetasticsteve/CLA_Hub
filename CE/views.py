from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from CE.models import CultureEvent, TextModel, PictureModel, ParticipationModel, QuestionModel
from taggit.models import Tag
from CE.forms import CE_EditForm, PictureUploadForm, question_form_set, text_form_set
from CE.settings import culture_events_shown_on_home_page
from CE import OCM_categories


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
    ce = get_object_or_404(CultureEvent, pk=pk)
    if request.method == 'GET':
        form = CE_EditForm(initial= {
            'title' : ce.title,
            'participation' : ce.participation,
            'description' : ce.description,
            'differences' : ce.differences
        })
        picture_form = PictureUploadForm()

    elif request.method == 'POST':
        form = CE_EditForm(request.POST, instance=ce)
        picture_form = PictureUploadForm(request.POST, request.FILES)
        if form.is_valid():
            ce.title = form.cleaned_data['title']
            ce.participation = form.cleaned_data['participation']
            ce.description = form.cleaned_data['description']
            ce.pk = pk
            ce.last_modified_by = str(request.user)
            ce.interpretation = form.cleaned_data['interpretation']
            ce.variation = form.cleaned_data['variation']
            ce.save()
            messages.success(request, 'CE updated')
            if picture_form.is_valid():
                if picture_form.cleaned_data['picture']:
                    new_pic = PictureModel()
                    new_pic.ce = ce
                    new_pic.picture = picture_form.cleaned_data['picture']
                    new_pic.save()
            return redirect('CE:view', pk=ce.pk)
        # todo upload multiple files at once
        # todo changing pictures
        # todo rotating pictures

    # GET request
    texts = TextModel.objects.filter(ce_id=pk)
    # text_forms = []
    # for text in texts:
    #     text_forms.append(Text_EditForm(text))
    current_pics = PictureModel.objects.filter(ce_id=pk)
    # todo add a new text button

    context = {
    # key values are called by template
        'CE': ce,
        'Texts': texts,
        'Form': form,
        'PictureUpload': picture_form,
        'CurrentPics': current_pics
    }
    return render(request, 'CE/edit_CE.html', context)


@ login_required
def new(request):
    template = 'CE/new_CE.html'
    if request.method == 'GET':
        form = CE_EditForm()
        picture_form = PictureUploadForm()
        text_form = text_form_set(prefix='text')
        question_form = question_form_set(prefix='question')

        context = {
            'Form': form,
            'PictureUpload': picture_form,
            'TextForm': text_form,
            'QuestionForm' : question_form
        }
        return render(request, template, context)

    elif request.method == 'POST':
        form = CE_EditForm(request.POST)
        picture_form = PictureUploadForm(request.POST, request.FILES)
        text_form = text_form_set(request.POST, request.FILES, prefix='text')
        question_form = question_form_set(request.POST, prefix='question')
        if form.is_valid():
            ce = form.save(request)
            if picture_form.is_valid():
                picture_form.save(ce)
            for t_form in text_form:
                if t_form.is_valid():
                    t_form.save(ce)
            for question in question_form:
                if question.is_valid():
                    question.save(ce, request)
            return redirect('CE:view', pk=ce.pk)

        else:
            context = {
                'Form' : form,
                'PictureUpload': picture_form,
                'TextForm' : text_form,
                'QuestionForm' : question_form
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
        'Tags':tags
    }
    return render(request, template, context)