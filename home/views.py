from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .forms import ContactForm, TutorForm
from .models import Tutor

def index(request):
    """A view to return the index page"""
    return render(request, "home/index.html")

def about(request):
    """A view to render the about page"""
    tutors = Tutor.objects.all()
    return render(request, "includes/about.html", {"tutors": tutors})

def manage_tutors(request):
    tutors = Tutor.objects.all()
    form = TutorForm()

    if request.method == "POST":
        form = TutorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Tutor added successfully.")
            return redirect("manage_tutors")

    context = {
        "tutors": tutors,
        "form": form,
    }
    return render(request, "tutors/manage_tutors.html", context)

def edit_tutor(request, pk):
    tutor = get_object_or_404(Tutor, pk=pk)
    if request.method == "POST":
        form = TutorForm(request.POST, request.FILES, instance=tutor)
        if form.is_valid():
            form.save()
            messages.success(request, "Tutor updated successfully.")
            return redirect("manage_tutors")
    else:
        form = TutorForm(instance=tutor)
    return render(request, "tutors/edit_tutor.html", {"form": form, "tutor": tutor})

def delete_tutor(request, pk):
    tutor = get_object_or_404(Tutor, pk=pk)
    if request.method == "POST":
        tutor.delete()
        messages.success(request, "Tutor deleted.")
        return redirect("manage_tutors")
    return render(request, "tutors/confirm_delete.html", {"tutor": tutor})

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
