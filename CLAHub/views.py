from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from CLAHub import forms
from CLAHub.tools import import_profiles_from_csv


def home(request):
    return render(request, 'CLAHub_home.html')


@login_required
def tools(request):
    return render(request, 'tools.html')


@login_required
def import_profiles(request):
    if request.method == 'POST':
        form = forms.ProfileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            import_profiles_from_csv(request.FILES['file'])
            messages.success(request, 'Import successful')
            return redirect('home')
    form = forms.ProfileUploadForm()
    context = {
        'form': form
    }
    return render(request, 'import_profiles.html', context)
