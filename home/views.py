from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .forms import ContactForm


def index(request):
    """A view to return the index page"""

    return render(request, "home/index.html")


def about(request):
    """A view to render the about page"""
    return render(request, "includes/about.html")


def contact(request):
    """A view to render the contact page and handle form submissions"""
    form = ContactForm()

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            message = (
                f"Message from: {form.cleaned_data['name']} <{form.cleaned_data['email']}>\n\n"
                f"{form.cleaned_data['message']}"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully!")
            return render(request, "includes/contact.html", {"form": ContactForm()})

    return render(request, "includes/contact.html", {"form": form})
