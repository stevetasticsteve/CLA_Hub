from django.shortcuts import render, get_object_or_404, redirect
from CE.models import CultureEvent, Texts
from CE.forms import CE_EditForm

def home_page(request):
    return render(request, 'CE/home_page.html')

def edit_CE_page(request, pk):
    ce = get_object_or_404(CultureEvent, pk=pk)
    form = CE_EditForm(initial= {
        'title' : ce.title,
        'participation' : ce.participation,
        'description' : ce.description,
        'differences' : ce.differences
    })

    if request.method == 'POST':
        form = CE_EditForm(request.POST)
        if form.is_valid():
            ce.title = form.cleaned_data['title']
            ce.participation = form.cleaned_data['participation']
            ce.description = form.cleaned_data['description']
            ce.save()

            return redirect('view_CE', pk=pk)

    # GET request
    texts = Texts.objects.filter(ce_id=pk)
    context = {
    # key values are called by template
        'CE' : ce,
        'Texts' : texts,
        'Form' : form
    }

    return render(request, 'CE/edit_CE.html', context)

def view_CE_page(request, pk):
    ce = get_object_or_404(CultureEvent, pk=pk)
    texts = Texts.objects.filter(ce_id=pk)
    context = {
        'CE' : ce,
        'Texts' : texts
    }
    return render(request, 'CE/view_CE.html', context)

# def new_CE_page(request):
#     form = CE_EditForm()
#     context = {
#         'Form' : form
#     }
#
#     return render(request, 'CE/edit_CE.html', context)