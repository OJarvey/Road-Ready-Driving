from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .forms import OrderForm
from .models import Order, OrderLineItem
from packages.models import Package
from bag.contexts import bag_contents
from django.db import models

import json
import stripe

@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user.username if request.user.is_authenticated else 'Anonymous',
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)

def update_total(self):
    total = self.lineitems.aggregate(total_sum=models.Sum('lineitem_total'))['total_sum'] or 0
    self.order_total = total
    self.grand_total = total
    self.save(update_fields=['order_total', 'grand_total'])
    print(f"Updated totals for order {self.order_number}: order_total={self.order_total}, grand_total={self.grand_total}")

@require_POST
@csrf_exempt
def save_order(request):
    try:
        print("Received order data:", request.body)
        data = json.loads(request.body)
        bag = request.session.get("bag", {})
        print("Bag contents:", bag)

        if not bag:
            return JsonResponse({"success": False, "error": "Bag is empty"}, status=400)

        order_form = OrderForm(data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.order_number = order._generate_order_number()
            if "payment_intent_id" in data:
                order.stripe_payment_intent_id = data["payment_intent_id"]
            order.save()
            print(f"Order Created: {order.order_number}")

            for item_id, quantity in bag.items():
                item_id = int(item_id)
                package = Package.objects.get(pk=item_id)
                print(f"Package: {package.name}, Qty: {quantity}")
                print(f"Type of package: {type(package)}")
                print(f"Insance check: {isinstance(package, Package)}")

                
                order_line_item = OrderLineItem(order=order, package_id=package.pk, quantity=quantity)
                order_line_item.save()
                print(f"Line item added: {package.name}, Qty: {quantity}, Lineitem_total: {order_line_item.lineitem_total}")

            order.update_total()
            print(f"Final totals: order_total={order.order_total}, grand_total={order.grand_total}")

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

    # Prepare Stripe PaymentIntent and context (used for both GET and POST error cases)
    current_bag = bag_contents(request)
    total = current_bag["total"]
    stripe_total = round(total * 100)
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )
    order_form = OrderForm()

    if request.method == "POST":
        # Get form data
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

            try:
                # Add line items
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
                    "One of the packages in your bag wasn't found in our database. Please try again or contact support.",
                )
                order.delete()
                return redirect(reverse("view_bag"))

            # Update totals
            order.update_total()

            # Store save-info in session if requested
            if "save-info" in request.POST:
                request.session["save_info"] = True
            else:
                request.session["save_info"] = False

            # Clear the bag and redirect to success
            request.session["bag"] = {}
            return redirect(reverse("checkout_success", args=[order.order_number]))
        else:
            # Form invalid: re-render checkout page with error
            messages.error(
                request,
                "There was an error with your form. Please check your details and try again.",
            )
            context = {
                "order_form": order_form,  # Pass the form with errors
                "stripe_public_key": stripe_public_key,
                "client_secret": intent.client_secret,
            }
            return render(request, "checkout/checkout.html", context)

    # GET request: Render checkout page with Stripe setup
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
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')
    
    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }
    return render(request, template, context)
