from django.db import models

class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'
    name = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.name
    
    def get_friendly_name(self):
        return self.name


class Package(models.Model):
    CATEGORY_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="packages")
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=100)  # Stores the icon name like "bronze-driving-icon"
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    image_url = models.URLField(max_length=500, blank=True, null=True)  # Stores hosted image URL
    image = models.ImageField(upload_to="packages/", blank=True, null=True)  # Stores uploaded image

    def __str__(self):
        return f"{self.name} - {self.category.name}"
