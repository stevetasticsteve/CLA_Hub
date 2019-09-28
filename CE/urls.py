from django.urls import path
from CE import views

app_name = 'CE'
urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('<int:pk>/edit', views.edit, name='edit'),
    path('new', views.new, name='new'),
    path('ocm/<int:category_code>-<int:subcategory_code>', views.OCM_category, name='OCM_category'),
    path('ocm', views.OCM_home, name='OCM_home'),
    path('questions_chron', views.questions_chron, name='questions_chron'),
    path('questions_alph', views.questions_alph, name='questions_alph'),
    path('questions_recent', views.questions_recent, name='questions_recent'),
    path('questions_unanswered', views.questions_unanswered, name='questions_unanswered'),
    path('<int:pk>', views.view, name='view'),
    path('<slug:slug>', views.view_slug, name='view_slug'),

]
