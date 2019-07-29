from django.shortcuts import render

def home_page(request):
    return render(request, 'CE/home_page.html')

def edit_CE_page(request):
    return render(request, 'CE/edit.html')