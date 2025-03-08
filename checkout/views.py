from django.shortcuts import render, redirect, reverse, get_object_or_404
import json
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt 

from .forms import OrderForm
from .models import Order, OrderLineItem
from packages.models import Package
from bag.contexts import bag_contents

import stripe

@require_POST
@csrf_exempt  # Use with caution; ideally, include CSRF token properly
def save_order(request):
    try:
        # Parse the JSON data from the AJAX request
        data = json.loads(request.body)
        bag = request.session.get("bag", {})

        # Create the order
        order_form = OrderForm(data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.order_number = order._generate_order_number()
            order.save()

            # Add line items from the bag
            for item_id, quantity in bag.items():
                package = get_object_or_404(Package, id=item_id)
                order_line_item = OrderLineItem(
                    order=order,
                    package=package,
                    quantity=quantity,
                )
                order_line_item.save()

            # Optionally save Stripe payment intent ID if available
            # You might want to pass this from the frontend
            if "payment_intent_id" in data:
                order.stripe_payment_intent_id = data["payment_intent_id"]
                order.save()

            # Clear the bag
            if "bag" in request.session:
                del request.session["bag"]

            return JsonResponse({"success": True, "order_number": order.order_number})
        else:
            return JsonResponse({"success": False, "error": "Invalid form data"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # Ensure the bag is not empty
    bag = request.session.get("bag", {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment.")
        return redirect(reverse("packages"))

    if request.method == "POST":
        form_data = {
            "full_name": request.POST["full_name"],
            "email": request.POST["email"],
            "phone_number": request.POST["phone_number"],
            "country": request.POST["country"],
            "postcode": request.POST["postcode"],
            "town_or_city": request.POST["town_or_city"],
            "street_address1": request.POST["street_address1"],
            "street_address2": request.POST["street_address2"],
        }

        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.order_number = order._generate_order_number()  # Ensure order number is generated
            order.save()  # Save before adding items

            # Add line items
            for item_id, quantity in bag.items():
                package = get_object_or_404(Package, pk=item_id)
                order_line_item = OrderLineItem.objects.create(
                    order=order, 
                    package=package, 
                    quantity=quantity
                )
                order_line_item.save()

            request.session["bag"] = {}  # Clear session bag after checkout

            return redirect(reverse("checkout_success", args=[order.order_number]))

        else:
            messages.error(request, "There was an error with your form. Please try again.")

    # Set up Stripe Payment
    current_bag = bag_contents(request)
    total = current_bag["total"]
    stripe_total = round(total * 100)
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    order_form = OrderForm()

    context = {
        "order_form": order_form,
        "stripe_public_key": stripe_public_key,
        "client_secret": intent.client_secret,
    }

    return render(request, "checkout/checkout.html", context)

def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    order = get_object_or_404(Order, order_number=order_number)

    messages.success(
        request,
        f"Booking successful! Your order number is {order_number}. A confirmation email has been sent to {order.email}.",
    )

    if "bag" in request.session:
        del request.session["bag"]

    template = "checkout/checkout_success.html"
    context = {
        "order": order,
    }

    return render(request, template, context)
