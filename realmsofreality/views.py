from django.shortcuts import render

def ror_home(request):
    template = 'ror/realms_of_reality.html'

    return render(request, template)