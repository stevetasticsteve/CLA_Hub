from django.urls import path
from realmsofreality import views

app_name = 'realmsofreality'
urlpatterns = [
    path('', views.ror_home, name='ror_home'),
    ]