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
def save_order(request):
    try:
        print("Received order data:", request.body)
        data = json.loads(request.body)
        bag = request.session.get("bag", {})

        if not bag:
            return JsonResponse({"success": False, "error": "Bag is empty"}, status=400)

        order_form = OrderForm(data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.order_number = order._generate_order_number()  # Ensure unique order number
            if "payment_intent_id" in data:
                order.stripe_payment_intent_id = data["payment_intent_id"]
            order.save()
            print(f"Order Created: {order.order_number}")

            for item_id, quantity in bag.items():
                package = get_object_or_404(Package, pk=item_id)
                order_line_item = OrderLineItem(
                    order=order,
                    package=package,
                    quantity=quantity,
                    lineitem_total=package.price * quantity,
                )
                order_line_item.save()
                print(f"Line item added: {package.name}, Qty: {quantity}")

            # Update totals
            order.update_total()
            print(f"Totals: order_total={order.order_total}, grand_total={order.grand_total}")

            request.session["bag"] = {}
            return JsonResponse({"success": True, "order_number": order.order_number})
        else:
            print("Order form errors:", order_form.errors)
            return JsonResponse({"success": False, "error": order_form.errors.as_json()}, status=400)
    except Exception as e:
        print("Error saving order:", str(e))
        return JsonResponse({"success": False, "error": str(e)}, status=500)

def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    bag = request.session.get("bag", {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment.")
        return redirect(reverse("packages"))

    if request.method == "POST":
        # Handle traditional form submission (optional fallback)
        form_data = {
            "full_name": request.POST.get("full_name"),
            "email": request.POST.get("email"),
            "phone_number": request.POST.get("phone_number"),
            "country": request.POST.get("country"),
            "postcode": request.POST.get("postcode"),
            "town_or_city": request.POST.get("town_or_city"),
            "street_address1": request.POST.get("street_address1"),
            "street_address2": request.POST.get("street_address2"),
            "county": request.POST.get("county", ""),
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.order_number = order._generate_order_number()
            order.save()

            for item_id, quantity in bag.items():
                package = get_object_or_404(Package, id=item_id)
                OrderLineItem.objects.create(
                    order=order, package=package, quantity=quantity
                )
            request.session["bag"] = {}
            return redirect(reverse("checkout_success", args=[order.order_number]))
        else:
            messages.error(request, "There was an error with your form. Please try again.")
            # Fall through to render the form again with errors

    # GET request: Render checkout page with Stripe setup
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
    return render(request, "checkout/checkout.html", context)  # Always return a response

def checkout_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(
        request,
        f"Booking successful! Your order number is {order_number}. A confirmation email has been sent to {order.email}.",
    )
    if "bag" in request.session:
        del request.session["bag"]
    return render(request, "checkout/checkout_success.html", {"order": order})