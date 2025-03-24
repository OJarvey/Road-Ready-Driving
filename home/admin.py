from django.contrib import admin
from .models import Tutor


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ("name", "age", "experience",
                    "qualification", "success_rate")
