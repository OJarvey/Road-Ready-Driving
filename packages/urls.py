from django.urls import path
from . import views

urlpatterns = [
    path('packages/', views.all_packages, name='packages')
]
