from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_packages, name='packages')
]
