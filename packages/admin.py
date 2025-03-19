from django.contrib import admin
from .models import Category, Package


# Register your models here.
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "image",
    )

    ordering = ("category",)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Package, PackageAdmin)
