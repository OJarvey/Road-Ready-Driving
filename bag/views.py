from django.shortcuts import render, redirect, get_object_or_404
from packages.models import Package

# Create your views here.
def view_bag(request):
    """ A view to return the bag page """
    bag = request.session.get('bag', {})
    bookings = []
    total = 0

    for item_id, quantity in bag.items():
        package = get_object_or_404(Package, pk=item_id)
        line_total = package.price * quantity
        total += line_total
        bookings.append({
            'package': package,
            'quantity': quantity,
            'line_total': line_total,
        })

    context = {
        'bookings': bookings,
        'total': total,
    }

    return render(request, 'bag/bag.html', context)

def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url', '/')  # Provide a default path

    if not redirect_url:
        redirect_url = '/'  # Ensure there's always a redirect URL, adjust '/' to your desired default

    bag = request.session.get('bag', {})

    if item_id in list(bag.keys()):
        bag[item_id] += quantity
    else:
        bag[item_id] = quantity

    request.session['bag'] = bag
    return redirect(redirect_url)