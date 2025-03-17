from django import forms
from .models import Package, Category
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]
        self.fields["category"].choices = friendly_names

        self.fields["price"].widget.attrs.update(
            {
                "min": "0",
                "max": "2000",
                "step": "0.01",
            }
        )

        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "border-black rounded-2"
            if field.required:
                field.widget.attrs["required"] = "required"

        self.helper = FormHelper()
        self.helper.form_method = "post"
        submit_text = "Update Package" if kwargs.get("instance") else "Add Package"
        self.helper.add_input(
            Submit("submit", submit_text, css_class="btn btn-outline-secondary btn-sm")
        )
        self.helper.add_input(
            Submit(
                "cancel",
                "Cancel",
                css_class="btn btn-outline-secondary btn-sm",
                formnovalidate="formnovalidate",
                onclick="window.location='{% url 'packages' %}'; return false;",
            )
        )

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price > 2000:
            raise ValidationError("Price cannot exceed £2000.")
        return price
