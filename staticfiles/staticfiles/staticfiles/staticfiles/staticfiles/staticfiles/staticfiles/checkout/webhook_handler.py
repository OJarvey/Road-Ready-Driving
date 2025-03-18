from django.http import HttpResponse
from .models import Order, OrderLineItem
from packages.models import Package
from profiles.models import UserProfile
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

import json
import time

class StripeWH_Handler:
    """Handle Stripe webhooks for Road Ready Driving"""

    def __init__(self, request):
        self.request = request

    def send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order}
        ).strip()
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {
                'order': order,
                'contact_email': settings.DEFAULT_FROM_EMAIL,
            }
        )
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email],
            fail_silently=False,
        )

    def handle_event(self, event):
        return HttpResponse(content=f'Unhandled webhook received: {event["type"]}', status=200)

    def handle_payment_intent_succeeded(self, event):
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.get("bag")
        save_info = intent.metadata.get("save_info") == "true"
        username = intent.metadata.get("username")
        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        # Clean shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        try:
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1
                profile.default_street_address2 = shipping_details.address.line2
                profile.default_county = shipping_details.address.state
                profile.save()

            # Use shipping email if billing email is null, fallback to profile
            email = billing_details.email or shipping_details.email or profile.default_email

            order_exists = False
            attempt = 1
            while attempt <= 5:
                try:
                    order = Order.objects.get(
                        full_name__iexact=shipping_details.name,
                        email__iexact=email,
                        phone_number__iexact=shipping_details.phone,
                        country__iexact=shipping_details.address.country,
                        postcode__iexact=shipping_details.address.postal_code,
                        town_or_city__iexact=shipping_details.address.city,
                        street_address1__iexact=shipping_details.address.line1,
                        street_address2__iexact=shipping_details.address.line2,
                        county__iexact=shipping_details.address.state,
                        grand_total=grand_total,
                        stripe_payment_intent_id=pid,
                    )
                    order_exists = True
                    break
                except Order.DoesNotExist:
                    attempt += 1
                    time.sleep(1)

            if order_exists:
                self.send_confirmation_email(order)
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | SUCCESS: Verified driving lesson order already in database for {username}',
                    status=200
                )
            else:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    grand_total=grand_total,
                    stripe_payment_intent_id=pid,
                )
                for item_id, quantity in json.loads(bag).items():
                    package = Package.objects.get(id=int(item_id))
                    order_line_item = OrderLineItem(
                        order=order,
                        package=package,
                        quantity=quantity,
                    )
                    order_line_item.save()
                self.send_confirmation_email(order)
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | SUCCESS: Created driving lesson order for {username}',
                    status=200
                )
        except Exception as e:
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=500
            )

    def handle_payment_intent_payment_failed(self, event):
        intent = event.data.object
        username = intent.metadata.get("username")
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | Payment failed for driving lesson order by {username}',
            status=200
        )