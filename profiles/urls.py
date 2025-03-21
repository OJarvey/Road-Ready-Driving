from django.urls import path
from . import views
from .views import CustomLoginView, CustomLogoutView

urlpatterns = [
    path("",
         views.RedirectProfileView.as_view(),
         name="profile_redirect"
         ),
    path(
        "user/",
        views.UpdateUsernameView.as_view(),
        name="profile_user"
        ),
    path(
        "profile/",
        views.ProfileView.as_view(),
        name="profile"
        ),
    path(
        "orders/",
        views.OrderListView.as_view(),
        name="profile_orders"
        ),
    path(
        "orders/<str:order_number>/",
        views.OrderDetailView.as_view(),
        name="order_view"
    ),
    path(
        "delete/",
        views.delete_profile,
        name="delete_profile"
        ),
    path(
        "login/",
        CustomLoginView.as_view(),
        name="profile_login"
        ),
    path(
        "logout/",
        CustomLogoutView.as_view(),
        name="profile_logout"
        ),
]
