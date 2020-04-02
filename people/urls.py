from django.urls import path
from people import views

app_name = 'people'
urlpatterns = [
    path('', views.people_home, name='home'),
    path('<int:pk>', views.people_detail, name='detail'),
    path('new', views.new, name='new'),
    path('edit/<int:pk>', views.edit, name='edit'),
    path('search/', views.search_people, name='search'),
    path('alphabetically', views.alphabetically, name='alphabetically'),
    path('village/<int:village>', views.village, name='village'),
    path('help/family', views.help_family, name='family_help')
]