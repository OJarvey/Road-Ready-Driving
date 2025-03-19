from django import template
from django.urls import reverse

register = template.Library()


@register.filter
def get_url_path(url_name):
    try:
        return reverse(url_name)
    except Exception:
        return ""
