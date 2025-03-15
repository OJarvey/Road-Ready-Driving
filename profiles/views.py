from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from django.views.generic.base import RedirectView
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import UpdateUsernameForm, UserProfileForm
from checkout.models import Order
from .models import UserProfile
from allauth.account.forms import LoginForm
from django.contrib.auth import logout
from allauth.account.views import LoginView as AllauthLoginView
from allauth.account.views import LogoutView as AllauthLogoutView


class CustomLoginView(AllauthLoginView):
    template_name = "allauth/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        self.user = form.user
        login(self.request, self.user)

        messages.success(self.request, f"{self.user.username} has logged in successfully.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("profile")

class CustomLogoutView(AllauthLogoutView):
    template_name = "allauth/logout.html"  # Reuse your styled template

    def post(self, request, *args, **kwargs):
        # Log the user out
        logout(request)
        # Add custom success message
        messages.success(request, "User successfully logged out.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        # Redirect to login page after logout
        return reverse_lazy("account_login")

@method_decorator(login_required, name="dispatch")
class UpdateUsernameView(FormView):
    template_name = "profiles/update_username.html"
    form_class = UpdateUsernameForm
    success_url = reverse_lazy("profile_user")

    def get_form(self, form_class=None):
        return self.form_class(
            self.request.POST if self.request.method == "POST" else None,
            instance=self.request.user,
        )

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your username has been updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "There was an error updating your username. Please try again."
        )
        return super().form_invalid(form)


@method_decorator(login_required, name="dispatch")
class RedirectProfileView(RedirectView):
    pattern_name = "profile_user"

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_staff or self.request.user.is_superuser:
            self.pattern_name = "profile_user"
        else:
            self.pattern_name = "profile"
        return super().get_redirect_url(*args, **kwargs)


@method_decorator(login_required, name="dispatch")
class ProfileView(FormView):
    template_name = "profiles/profile.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("profile")

    def get_form(self, form_class=None):
        return self.form_class(
            instance=self.request.user.userprofile,
            data=self.request.POST if self.request.method == "POST" else None,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_form"] = self.get_form()
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your profile has been updated.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors and try again.")
        return super().form_invalid(form)


@method_decorator(login_required, name="dispatch")
class OrderListView(FormView):
    template_name = "profiles/orders.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("profile_orders")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            user_profile = self.request.user.userprofile
            context["orders"] = Order.objects.filter(
                user_profile=user_profile
            ).order_by("-date")
        except UserProfile.DoesNotExist:
            context["orders"] = Order.objects.none()
        return context


@method_decorator(login_required, name="dispatch")
class OrderDetailView(FormView):
    template_name = "profiles/order_detail.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("profile_orders")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(
            Order,
            order_number=self.kwargs["order_number"],
            user_profile=self.request.user.userprofile,
        )
        context["order"] = order
        return context

@login_required
def delete_profile(request):
    if request.method == "POST":
        # Confirm deletion and delete user + profile
        user = request.user
        user.delete()  # This deletes the User and cascades to UserProfile if on_delete=CASCADE
        messages.success(request, "Your profile has been successfully deleted.")
        return redirect("account_login")  # Redirect to login page after deletion
    return render(request, "profiles/delete_profile.html")