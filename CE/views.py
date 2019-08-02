from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from CE.models import CultureEvent, Texts, PictureModel
from CE.forms import CE_EditForm, Text_EditForm, PictureUploadForm
from CE.settings import culture_events_shown_on_home_page

def home_page(request):
    most_recent_ces = CultureEvent.objects.all().order_by(
        '-last_modified')[:culture_events_shown_on_home_page]
    context = {
        'CEs' : most_recent_ces
    }
    return render(request, 'CE/home_page.html', context)

def view(request, pk):
    # todo show pictures
    ce = get_object_or_404(CultureEvent, pk=pk)
    texts = Texts.objects.filter(ce_id=pk)
    context = {
        'CE' : ce,
        'Texts' : texts
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

    if request.method == 'POST':
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
                    print(picture_form.cleaned_data['picture'])
                    new_pic = PictureModel()
                    new_pic.ce = ce
                    new_pic.picture = picture_form.cleaned_data['picture']
                    new_pic.save()
            return redirect('CE:view', pk=ce.pk)
        # todo upload multiple files at once
        # todo image compression, pictures saved as they come. set to 1200x700 96 dpi
        # todo changing pictures
        # todo rotating pictures
        # todo better representation of pictures on edit screen

    # GET request
    texts = Texts.objects.filter(ce_id=pk)
    # text_forms = []
    # for text in texts:
    #     text_forms.append(Text_EditForm(text))
    current_pics = PictureModel.objects.filter(ce_id=pk)
    # todo include texts form same as pictures - optional
    # todo add a new text button

    context = {
    # key values are called by template
        'CE' : ce,
        'Texts' : texts,
        'Form' : form,
        'PictureUpload' : picture_form,
        'CurrentPics' : current_pics
        # 'TextForms' : text_forms
    }
    return render(request, 'CE/edit_CE.html', context)


@ login_required
def new(request):
    # todo add pictures and texts to new Ces
    if request.method == 'GET':
        form = CE_EditForm()

    if request.method == 'POST':
        form = CE_EditForm(request.POST)
        if form.is_valid():
            ce = CultureEvent()
            ce.title = form.cleaned_data['title']
            ce.participation = form.cleaned_data['participation']
            ce.description = form.cleaned_data['description']
            ce.last_modified_by = str(request.user)
            ce.save()
            return redirect('CE:view', pk=ce.pk)

    context = {
        'Form': form
    }
    return render(request, 'CE/new_CE.html', context)