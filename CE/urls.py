from django.urls import path
from . import views

app_name = 'CE'
urlpatterns = [
    path('', views.home_page, name='CE_Home'),
    path('<int:pk>/edit', views.edit_CE_page, name='edit_CE'),
    path('new', views.new_CE_page, name='new_CE'),
    path('<int:pk>', views.view_CE_page, name='view_CE')
]