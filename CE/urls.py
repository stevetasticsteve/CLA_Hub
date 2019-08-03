from django.urls import path
from CE import views

app_name = 'CE'
urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('<int:pk>/edit', views.edit, name='edit'),
    path('new', views.new, name='new'),
    path('<int:pk>', views.view, name='view')
]
