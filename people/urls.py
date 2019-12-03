from django.urls import path
from people import views

app_name = 'people'
urlpatterns = [
    path('', views.people_home, name='home'),
    path('<int:pk>', views.people_detail, name='detail'),
    path('new', views.new, name='new'),
    path('alphabetically', views.alphabetically, name='alphabetically'),
]