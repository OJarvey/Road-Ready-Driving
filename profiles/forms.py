from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class UpdateUsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "This username is already taken. Please choose another one."
            )
        return username


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ("user",)
        fields = (
            "default_full_name",
            "default_email",
            "default_phone_number",
            "default_country",
            "default_street_address1",
            "default_street_address2",
            "default_town_or_city",
            "default_county",
            "default_postcode",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "default_full_name": "Full Name",
            "default_email": "Email Address",
            "default_phone_number": "Phone Number",
            "default_postcode": "Postal Code",
            "default_town_or_city": "Town or City",
            "default_street_address1": "Street Address 1",
            "default_street_address2": "Street Address 2",
            "default_county": "County/State",
            "default_country": "Country",
        }
        self.fields["default_full_name"].widget.attrs["autofocus"] = True
        for field in self.fields:
            if field != "default_country":
                placeholder = (
                    f"{placeholders[field]} *"
                    if self.fields[field].required
                    else placeholders[field]
                )
                self.fields[field].widget.attrs["placeholder"] = placeholder
            self.fields[field].widget.attrs["class"] = "stripe-style-input"
            self.fields[field].label = False
