import uuid

from django.db import models
from django.db.models import Sum
from django.conf import settings
from django_countries.fields import CountryField

class Package(models.Model):
    name = models.CharField(max_length=50, blank=False)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False)

    def __str__(self):
        return self.name

class Order(models.Model):
    full_name = models.CharField(max_length=50, blank=False)
    phone_number = models.CharField(max_length=20, blank=False)
    country = models.CharField(max_length=40, blank=False)
    postcode = models.CharField(max_length=20, blank=True)
    town_or_city = models.CharField(max_length=40, blank=False)
    street_address1 = models.CharField(max_length=80, blank=False)
    street_address2 = models.CharField(max_length=80, blank=True)
    county = models.CharField(max_length=80, blank=True)
    date = models.DateField()
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  

    def _generate_order_number(self):
        return uuid.uuid4().hex.upper()
    
    def update_total(self):
        self.order.order_total = self.order.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0
        self.order.grand_total = self.order.order
        self.order.save()
    
    def save(self, *args, **kwargs):
        
        if not self.order.order_number:
            self.order.order_number = self._generate_order_number()
            self.order.save()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.order_number
        
class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False, on_delete=models.CASCADE, related_name='lineitems')
    package = models.ForeignKey(Package, null=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False, editable=False)
    
    def save(self, *args, **kwargs):
        self.lineitem_total = self.package.price * self.quantity
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'SKU {self.package.name} on order {self.order.order_number}'