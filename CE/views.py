from django.shortcuts import render, get_object_or_404, redirect
from CE.models import CultureEvent, Texts
from CE.forms import CE_EditForm, Text_EditForm
from CE.settings import culture_events_shown_on_home_page

def home_page(request):
    most_recent_ces = CultureEvent.objects.all().order_by(
        '-last_modified')[:culture_events_shown_on_home_page]
    context = {
        'CEs' : most_recent_ces
    }
    return render(request, 'CE/home_page.html', context)

def edit(request, pk):
    ce = get_object_or_404(CultureEvent, pk=pk)
    form = CE_EditForm(initial= {
        'title' : ce.title,
        'participation' : ce.participation,
        'description' : ce.description,
        'differences' : ce.differences
    })

    if request.method == 'POST':
        print('POST request recieved')
        form = CE_EditForm(request.POST)
        if form.is_valid():
            print('valid form')
            ce.title = form.cleaned_data['title']
            ce.participation = form.cleaned_data['participation']
            ce.description = form.cleaned_data['description']
            ce.save()

            return redirect('view_CE', pk=pk)

    # GET request
    texts = Texts.objects.filter(ce_id=pk)
    # text_forms = []
    # for text in texts:
    #     text_forms.append(Text_EditForm(text))
    context = {
    # key values are called by template
        'CE' : ce,
        'Texts' : texts,
        'Form' : form,
        # 'TextForms' : text_forms
    }

    return render(request, 'CE/edit_CE.html', context)

def view(request, pk):
    ce = get_object_or_404(CultureEvent, pk=pk)
    texts = Texts.objects.filter(ce_id=pk)
    context = {
        'CE' : ce,
        'Texts' : texts
    }
    return render(request, 'CE/view_CE.html', context)

def new(request):
    pass
#todo use a modelForm to create a new CE page
#     form = CE_EditForm()
#     context = {
#         'Form' : form
#     }
#
#     return render(request, 'CE/edit_CE.html', context)