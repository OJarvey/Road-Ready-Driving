from django.db import models
from cloudinary.models import CloudinaryField

class Tutor(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    experience = models.IntegerField(help_text="Years of experience")
    qualification = models.CharField(max_length=255)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2)
    image = CloudinaryField(
        'image', 
        folder='tutors', 
        default='notutor_bzsagz',
        transformation={'quality': 'auto'},
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name
