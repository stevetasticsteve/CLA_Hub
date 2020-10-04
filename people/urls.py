from django.urls import path
from people import views

app_name = 'people'
urlpatterns = [
    path('', views.people_home, name='home'),
    path('<int:pk>', views.people_detail, name='detail'),
    path('medical/<int:pk>', views.medical_profile, name='medical'),
    path('medical/<int:pk>/add', views.medical_assessment_add, name='new_assessment'),
    path('medical/<int:pk>/edit/<int:event_pk>', views.medical_assessment_edit, name='edit_assessment'),
    path('medical/<int:pk>/notes', views.edit_medical_notes, name='edit_medical_notes'),
    path('new', views.new, name='new'),
    path('edit/<int:pk>', views.edit, name='edit'),
    path('search/', views.search_people, name='search'),
    path('alphabetically', views.alphabetically, name='alphabetically'),
    path('village/<int:village>', views.village, name='village'),
    path('help/family', views.help_family, name='family_help')
]