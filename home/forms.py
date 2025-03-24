from django import forms
from .models import Tutor


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Your Name")
    email = forms.EmailField(required=True, label="Your Email")
    subject = forms.CharField(max_length=150, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)


class TutorForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = ["name", "age", "experience", "qualification", "success_rate", "image"]
