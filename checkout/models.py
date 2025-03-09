import uuid

from django.db import models
from packages.models import Package as ExternalPackage
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
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(max_length=254, blank=False)
    phone_number = models.CharField(max_length=20, blank=False)
    country = models.CharField(max_length=40, blank=False)
    street_address1 = models.CharField(max_length=80, blank=False)
    street_address2 = models.CharField(max_length=80, blank=True)
    town_or_city = models.CharField(max_length=40, blank=False)
    county = models.CharField(max_length=80, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    date = models.DateField(auto_now_add=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)

    def _generate_order_number(self):
        return uuid.uuid4().hex.upper()

    def update_total(self):
        total = self.lineitems.aggregate(total_sum=models.Sum('lineitem_total'))['total_sum'] or 0
        print(f"Line items count: {self.lineitems.count()}, Calculated total: {total}")
        self.order_total = total
        self.grand_total = total
        self.save(update_fields=['order_total', 'grand_total'])
        print(f"Updated totals for order {self.order_number}: order_total={self.order_total}, grand_total={self.grand_total}")

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False, on_delete=models.CASCADE, related_name='lineitems')
    package = models.ForeignKey(ExternalPackage, null=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=1)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        print("Saving OrderLineItem")
        print(f"Type of package inside save: {type(self.package)}")
        print(f"Insance check inside save: {isinstance(self.package, Package)}")
        print(f"Package ID inside save: {self.package.id}")
        
        self.lineitem_total = self.package.price * self.quantity
        print(f"Calculating lineitem_total: {self.package.name}, Price={self.package.price}, Qty={self.quantity}, Total={self.lineitem_total}")
        super().save(*args, **kwargs)
        self.order.update_total()

    def __str__(self):
        return f'Package {self.package.name} on order {self.order.order_number}'
