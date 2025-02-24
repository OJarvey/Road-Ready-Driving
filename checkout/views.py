from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


def checkout(request):
    bag = request.session.get("bag", {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse("packages"))
    
    order_form = OrderForm()
    template = "checkout/checkout.html"
    context = {
        "order_form": order_form,
        "stripe_public_key": "pk_test_51QfMYlIej1oYkeirpkQGTjVf5m72M27WW0C3C8SU1Wua61GgHhUpEoqfwvqsuYmdqvutm5UWgAk5GbOuR7wrY1NX00nRkeCezv",
        "client_secret": "test client secret",
    }
    return render(request, 'checkout/checkout.html', context)
