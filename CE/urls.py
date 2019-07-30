from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='CE_Home'),
    path('edit/<int:pk>', views.edit_CE_page, name='CE_Edit'),
    # path('edit/new', views.new_CE_page, name='new_CE'),
    path('<int:pk>', views.view_CE_page, name='view_CE')
]