from django.shortcuts import render
from CE.models import CultureEvent, Texts
from CE.forms import CE_EditForm

def home_page(request):
    return render(request, 'CE/home_page.html')

def edit_CE_page(request, pk):
    ce = CultureEvent.objects.get(pk=pk)
    form = CE_EditForm()

    # This section creates a new CE instead of updating an old one
    if request.method == 'POST':
        form = CE_EditForm(request.POST)
        if form.is_valid():
            ce.title = form.cleaned_data['title']
            ce.save()

    # GET request
    texts = Texts.objects.filter(culture_event=ce)
    context = {
    # key values are called by template
        'CE' : ce,
        'Texts' : texts,
        'Form' : form
    }

    return render(request, 'CE/edit_CE.html', context)

def view_CE_page(request, pk):
    ce = CultureEvent.objects.get(pk=pk)
    context = {
        'CE' : ce
    }
    return render(request, 'CE/view_CE.html', context)

# def new_CE_page(request):
#     form = CE_EditForm()
#     context = {
#         'Form' : form
#     }
#
#     return render(request, 'CE/edit_CE.html', context)