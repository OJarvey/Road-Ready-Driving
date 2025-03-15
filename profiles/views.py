from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from django.views.generic.base import RedirectView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import UpdateUsernameForm, UserProfileForm
from checkout.models import Order


class CustomLoginView(LoginView):
    template_name = "profiles/login.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("home")

    def form_valid(self, form):
        login(self.request, form.get_user())
        previous_page = self.request.session.pop("previous_page", None)
        return redirect(previous_page) if previous_page else super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if "next" not in request.GET:
            previous_page = request.META.get("HTTP_REFERER")
            if previous_page and previous_page != request.build_absolute_uri(
                reverse_lazy("account_login")
            ):
                request.session["previous_page"] = previous_page
        return super().get(request, *args, **kwargs)


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
            instance=self.request.user.userprofile, **self.get_form_kwargs()
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
        user_profile = self.request.user.userprofile
        context['orders'] = Order.objects.filter(user_profile=user_profile)
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
            user_profile=self.request.user,
        )
        context["order"] = order
        return context
