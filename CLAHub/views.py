from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from CLAHub import forms
from CLAHub.tools import import_profiles_from_csv
import logging

logger = logging.getLogger('CLAHub')


def home(request):
    context = {
        'title': 'CLAHub'
    }
    return render(request, 'CLAHub_home.html', context)


@login_required
def tools(request):
    context = {
        'title': 'Tools'
    }
    return render(request, 'tools.html', context)


@login_required
def import_profiles(request):
    # todo need to install celery so this can be processed asynchroniously
    if request.method == 'POST':
        form = forms.ProfileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            _import = import_profiles_from_csv(request.FILES['file'])
            if type(_import) == int:
                messages.success(request, 'Import successful, %s records imported' % (_import,))
                return redirect('home')
            elif _import == 'missing_data_error':
                messages.error(request, 'Data is missing, import cancelled')
            elif _import == 'village_spelling_error':
                messages.error(request, 'Import cancelled, a village name has been spelt incorrectly')
            elif _import.startswith('missing_file_error'):
                # get the filename by stripping off the internal error message
                missing_file = _import.lstrip('missing_file_error')
                messages.error(request, 'Import cancelled, %s not found in imports folder' % (missing_file,))
            else:
                messages.error(request, 'Import failed')

    form = forms.ProfileUploadForm()
    context = {
        'form': form,
        'title': 'Import profiles'
    }
    return render(request, 'import_profiles.html', context)
