from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'CLAHub_home.html')

@login_required
def tools(request):
    return render(request, 'tools.html')
