from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from CE.models import CultureEvent, TextModel, PictureModel, ParticipationModel, QuestionModel, Tags
from CE.forms import CE_EditForm, PictureUploadForm, ParticipantForm, question_form_set, text_form_set
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
    if request.method == 'GET':
        form = CE_EditForm()
        picture_form = PictureUploadForm()
        participant_form = ParticipantForm()
        text_form = text_form_set(request.GET or None, prefix='text')
        question_form = question_form_set(request.GET or None, prefix='question')

        context = {
            'Form': form,
            'PictureUpload': picture_form,
            'ParticipantForm': participant_form,
            'TextForm': text_form,
            'QuestionForm' : question_form
        }
        return render(request, 'CE/new_CE.html', context)

    elif request.method == 'POST':
        form = CE_EditForm(request.POST)
        picture_form = PictureUploadForm(request.POST, request.FILES)
        participant_form = ParticipantForm(request.POST)
        text_form = text_form_set(request.POST, request.FILES, prefix='text')
        question_form = question_form_set(request.POST, prefix='question')
        if form.is_valid():
            ce = CultureEvent()
            ce.title = form.cleaned_data['title']
            ce.description_plain_text = form.cleaned_data['description_plain_text']
            ce.last_modified_by = str(request.user)

            if participant_form.is_valid():
                ce.save()
                newtag = Tags()
                newtag.tag = form.cleaned_data['tags']
                newtag.save()
                ce.tags.add(newtag)
                participants = ParticipationModel()
                participants.ce = ce
                participants.team_participants = participant_form.cleaned_data['team_participants']
                participants.national_participants = participant_form.cleaned_data['national_participants']
                participants.date = participant_form.cleaned_data['date']
                participants.save()
                messages.success(request, 'New CE created')
        else:
            context = {
                'Form' : form,
                'PictureUpload': picture_form,
                'ParticipantForm': participant_form,
                'TextForm' : text_form,
                'QuestionForm' : question_form
            }
            return render(request, 'CE/new_CE.html', context)
        if picture_form.is_valid():
            if picture_form.cleaned_data['picture']:
                new_pic = PictureModel()
                new_pic.ce = ce
                new_pic.picture = picture_form.cleaned_data['picture']
                new_pic.save()
        for t_form in text_form:
            if t_form.is_valid():
                if t_form.cleaned_data:
                    new_text = TextModel()
                    new_text.ce = ce
                    new_text.orthographic_text = t_form.cleaned_data['orthographic_text']
                    new_text.phonetic_text = t_form.cleaned_data['phonetic_text']
                    if t_form.cleaned_data['phonetic_text']:
                        if t_form.cleaned_data['phonetic_standard'] == '':
                            new_text.phonetic_standard = 1
                        else:
                            new_text.phonetic_standard = t_form.cleaned_data['phonetic_standard']
                    if t_form.cleaned_data['valid_for_DA']:
                        new_text.valid_for_DA = True
                        new_text.discourse_type = t_form.cleaned_data['discourse_type']
                    else:
                        new_text.valid_for_DA = False
                    new_text.audio = t_form.cleaned_data['audio']
                    new_text.save()
        for question in question_form:
            if question.is_valid():
                if question.cleaned_data:
                    new_question = QuestionModel()
                    new_question.ce = ce
                    new_question.asked_by = str(request.user)
                    new_question.last_modified_by = str(request.user)
                    new_question.question = question.cleaned_data['question']
                    new_question.answer = question.cleaned_data['answer']
                    if question.cleaned_data['answer']:
                        new_question.answered_by = str(request.user)
                    new_question.save()
                    #todo write question tests

        return redirect('CE:view', pk=ce.pk)


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
        'OCM_categories': OCM_categories.OCM_categories,
        'OCM_sub_categories': OCM_categories.OCM_sub_categories
    }
    return render(request, template, context)


def OCM_category(request, category_code, subcategory_code):
    template = 'CE/OCM_category.html'
    context = {
        'code': category_code,
        'sub': subcategory_code
    }

    return render(request, template, context)