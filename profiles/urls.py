from django.urls import path
from . import views

urlpatterns = [
    path('', views.RedirectProfileView.as_view(), name='profile_redirect'),
    path('user/', views.UpdateUsernameView.as_view(), name='profile_user'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('orders/', views.OrderListView.as_view(), name='profile_orders'),
    path('orders/<str:order_number>/', views.OrderDetailView.as_view(), name='order_view'),
]