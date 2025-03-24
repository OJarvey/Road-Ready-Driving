from django.db import models
from django.contrib import messages
from cloudinary.models import CloudinaryField


class Category(models.Model):
    class Meta:
        verbose_name_plural = "Categories"

    name = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.name


class Package(models.Model):
    CATEGORY_CHOICES = [
        ("bronze", "Bronze"),
        ("silver", "Silver"),
        ("gold", "Gold"),
    ]

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="packages"
    )
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(
        max_length=100
    )  # Stores the icon name like "bronze-driving-icon"
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    image = CloudinaryField(
        "image",
        blank=True,
        null=True,
        folder="packages",
        transformation={
            "width": 1024,
            "height": 1024,
            "crop": "fill",
            "gravity": "auto",
            "fetch_format": "auto",
            "quality": "auto",
        },)
    # Stores Cloudinary public_id and resizes image to 1024x1024

    image_url = models.URLField(max_length=500, blank=True, null=True)
    # Stores Cloudinary image URL

    def __str__(self):
        return f"{self.name} - {self.category.name}"

    def delete(self, *args, **kwargs):
        """Override delete to handle existing bag items"""
        # Clean up bags containing this package
        import cloudinary.uploader
        from bag.contexts import bag_contents
        from django.contrib.sessions.models import Session
        from django.utils import timezone

        # Clean up bags containing this package
        active_sessions = Session.objects.filter(
            expire_date__gte=timezone.now())
        for session in active_sessions:
            if "bag" in session.get_decoded():
                bag = session.get_decoded()["bag"]
                if str(self.id) in bag:
                    del bag[str(self.id)]
                    session.session_data = Session.objects.encode(bag)
                    session.save()

            if self.image:
                cloudinary.uploader.destroy(self.image.public_id)

        super().delete(*args, **kwargs)
