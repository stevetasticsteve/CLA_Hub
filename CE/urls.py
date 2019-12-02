from django.urls import path
from CE import views

app_name = 'CE'
urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('alphabetical', views.alphabetical, name='alphabetical'),
    path('<int:pk>/edit', views.edit, name='edit'),
    path('new', views.new, name='new'),
    path('ocm', views.OCM_home, name='OCM_home'),
    path('texts/genre/<int:genre>', views.text_genre, name='text_genre'),
    path('texts', views.texts_home, name='texts_home'),
    path('tag/<slug:slug>', views.tag_detail_page, name='view_tag'),
    path('tag', views.tag_list_page, name='list_tags'),
    path('questions_chron', views.questions_chron, name='questions_chron'),
    path('questions_alph', views.questions_alph, name='questions_alph'),
    path('questions_recent', views.questions_recent, name='questions_recent'),
    path('questions_unanswered', views.questions_unanswered, name='questions_unanswered'),
    path('<int:pk>', views.view, name='view'),
    path('search/', views.search_CE, name='search_CE'),
    path('<slug:slug>', views.view_slug, name='view_slug'),
]
