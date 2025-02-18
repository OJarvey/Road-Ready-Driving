from django.urls import path
from . import views
from .views import add_to_bag

urlpatterns = [
    path('', views.view_bag, name='view_bag'),
    path('add/<int:item_id>/', views.add_to_bag, name='add_to_bag'),
]
