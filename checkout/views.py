from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .forms import OrderForm
from .models import Order, OrderLineItem
from packages.models import Package
from bag.contexts import bag_contents
from profiles.models import UserProfile

import json
import stripe


@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get("client_secret").split("_secret")[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(
            pid,
            metadata={
                "bag": json.dumps(request.session.get("bag", {})),
                "save_info": request.POST.get("save_info", "false"),
                "username": request.user.username,
            },
        )
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(
            request,
            "Sorry, your payment cannot be processed right now. "
            "Please try again later."
        )
        return HttpResponse(content=str(e), status=400)


@require_POST
@csrf_exempt
def save_order(request):
    try:
        print("Received order data:", request.body)
        data = json.loads(request.body)
        bag = request.session.get("bag", {})
        print("Bag contents:", bag)

        if not bag:
            return JsonResponse({"success": False,
                                 "error": "Bag is empty"}, status=400)

        order_form = OrderForm(data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.order_number = order._generate_order_number()
            if "payment_intent_id" in data:
                order.stripe_payment_intent_id = data["payment_intent_id"]
            order.user_profile = request.user.userprofile
            order.save()
            print(f"Order Created: {order.order_number}")

            for item_id, quantity in bag.items():
                package = Package.objects.get(pk=int(item_id))
                order_line_item = OrderLineItem(
                    order=order, package=package, quantity=quantity
                )
                order_line_item.save()
                print(
                    f"Line item added: {package.name}, "
                    f"Qty: {quantity}, "
                    f"Total: {order_line_item.lineitem_total}"
                )

            order.update_total()
            print(
                f"Final totals: " \
                f"order_total={order.order_total}, " \
                f"grand_total={order.grand_total}"
            )

            # Update UserProfile with order details
            profile = request.user.userprofile
            profile.default_full_name = order.full_name
            profile.default_email = order.email
            profile.default_phone_number = order.phone_number
            profile.default_country = order.country
            profile.default_street_address1 = order.street_address1
            profile.default_street_address2 = order.street_address2
            profile.default_town_or_city = order.town_or_city
            profile.default_county = order.county
            profile.default_postcode = order.postcode
            profile.save()
            print(f"Updated UserProfile for {request.user.username}")

            request.session["bag"] = {}
            return JsonResponse({"success": True,
                                 "order_number": order.order_number})
        else:
            print("Order form errors:", order_form.errors)
            return JsonResponse(
                {"success": False, "error": order_form.errors.as_json()},
                status=400
            )
    except Exception as e:
        print("Error saving order:", str(e))
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required(login_url="account_login")
def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    bag = request.session.get("bag", {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment.")
        return redirect(reverse("packages"))

    # Prepare Stripe PaymentIntent
    current_bag = bag_contents(request)
    total = current_bag["total"]
    processing_fee = current_bag["processing_fee"]
    grand_total = current_bag["grand_total"]

    # Prepare Stripe PaymentIntent with grand_total
    stripe_total = round(total * 100)
    stripe.api_key = stripe_secret_key
    stripe_total = round(grand_total * 100)
    profile = request.user.userprofile
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
        metadata={
            "bag": json.dumps(bag),
            "save_info": "false",
            "username": request.user.username,
        },
        shipping={  # Add shipping details from profile initially
            "name": profile.default_full_name or request.user.username,
            "address": {
                "line1": profile.default_street_address1 or "",
                "line2": profile.default_street_address2 or "",
                "city": profile.default_town_or_city or "",
                "state": profile.default_county or "",
                "postal_code": profile.default_postcode or "",
                "country": profile.default_country or "",
            },
            "phone": profile.default_phone_number or "",
        },
    )

    # Prepopulate form with UserProfile data
    initial_data = {
        "full_name": profile.default_full_name,
        "email": profile.default_email or request.user.email,
        "phone_number": profile.default_phone_number,
        "country": profile.default_country,
        "street_address1": profile.default_street_address1,
        "street_address2": profile.default_street_address2,
        "town_or_city": profile.default_town_or_city,
        "county": profile.default_county,
        "postcode": profile.default_postcode,
    }
    order_form = OrderForm(initial=initial_data)

    if request.method == "POST":
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
            order.user_profile = profile
            order.stripe_payment_intent_id = intent.id
            order.save()

            # Update PaymentIntent with shipping details from form
            stripe.PaymentIntent.modify(
                intent.id,
                shipping={
                    "name": order.full_name,
                    "address": {
                        "line1": order.street_address1,
                        "line2": order.street_address2 or "",
                        "city": order.town_or_city,
                        "state": order.county or "",
                        "postal_code": order.postcode or "",
                        "country": order.country,
                    },
                    "phone": order.phone_number or "",
                },
            )

            try:
                for item_id, quantity in bag.items():
                    package = get_object_or_404(Package, pk=int(item_id))
                    OrderLineItem.objects.create(
                        order=order,
                        package=package,
                        quantity=quantity,
                    )
            except Package.DoesNotExist:
                messages.error(
                    request,
                "One of the packages in your bag wasn't found in our database."
                \
                "Please try again or contact support."
                )
                order.delete()
                return redirect(reverse("view_bag"))

            order.update_total()

            # Update UserProfile if save-info is checked
            if request.POST.get("save-info"):
                profile.default_full_name = order.full_name
                profile.default_email = order.email
                profile.default_phone_number = order.phone_number
                profile.default_country = order.country
                profile.default_street_address1 = order.street_address1
                profile.default_street_address2 = order.street_address2
                profile.default_town_or_city = order.town_or_city
                profile.default_county = order.county
                profile.default_postcode = order.postcode
                profile.save()
                print(f"Updated UserProfile for {request.user.username}")

            request.session["save_info"] = bool(request.POST.get("save-info"))
            request.session["bag"] = {}
            return redirect(reverse("checkout_success",
                                    args=[order.order_number]))
        else:
            messages.error(
                request,
                "There was an error with your form. "
                "Please check your details and try again."
            )

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
    save_info = request.session.get("save_info", False)
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(
        request,
        f"Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.",
    )

    if "bag" in request.session:
        del request.session["bag"]

    template = "checkout/checkout_success.html"
    context = {
        "order": order,
    }
    return render(request, template, context)
