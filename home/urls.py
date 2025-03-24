from django.urls import path
from . import views
from .views import about

urlpatterns = [
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("manage-tutors/", views.manage_tutors, name="manage_tutors"),
    path("manage-tutors/edit/<int:pk>/", views.edit_tutor, name="edit_tutor"),
    path("manage-tutors/delete/<int:pk>/", views.delete_tutor, name="delete_tutor"),
]
