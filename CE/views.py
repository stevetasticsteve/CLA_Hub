from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from CE.models import CultureEvent, TextModel, PictureModel, ParticipationModel
from CE.forms import CE_EditForm, PictureUploadForm, ParticipantForm, TextForm, text_form_set
from CE.settings import culture_events_shown_on_home_page

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
    context = {
        'CE' : ce,
        'Texts' : texts,
        'Pics' : pictures,
        'Participants' : participants
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
        # 'TextForms': text_forms
    }
    return render(request, 'CE/edit_CE.html', context)


@ login_required
def new(request):
    if request.method == 'GET':
        form = CE_EditForm()
        picture_form = PictureUploadForm()
        participant_form = ParticipantForm()
        text_form = text_form_set(request.GET or None)

    elif request.method == 'POST':
        form = CE_EditForm(request.POST)
        picture_form = PictureUploadForm(request.POST, request.FILES)
        participant_form = ParticipantForm(request.POST)
        text_form = text_form_set(request.POST, request.FILES)
        if form.is_valid():
            ce = CultureEvent()
            ce.title = form.cleaned_data['title']
            ce.description_plain_text = form.cleaned_data['description_plain_text']
            ce.last_modified_by = str(request.user)

            if participant_form.is_valid():
                ce.save()
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
                'TextForm' : text_form
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
                    if t_form.cleaned_data['phonetic_standard']:
                        new_text = TextModel()
                        new_text.ce = ce
                        new_text.orthographic_text = t_form.cleaned_data['orthographic_text']
                        new_text.phonetic_text = t_form.cleaned_data['phonetic_text']
                        new_text.phonetic_standard = t_form.cleaned_data['phonetic_standard']
                        new_text.audio = t_form.cleaned_data['audio']
                        new_text.save()

        return redirect('CE:view', pk=ce.pk)

    context = {
        'Form': form,
        'PictureUpload': picture_form,
        'ParticipantForm': participant_form,
        'TextForm' : text_form
    }
    return render(request, 'CE/new_CE.html', context)


