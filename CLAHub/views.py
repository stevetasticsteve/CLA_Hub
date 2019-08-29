from django.shortcuts import render

def home(request):
    return render(request, 'CLAHub_home.html')