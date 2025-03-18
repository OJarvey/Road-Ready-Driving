from django.urls import path
from . import views
from .views import about

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', about, name='about'),
    path('contact/', about, name='contact'),
]
