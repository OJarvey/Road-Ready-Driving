from django.shortcuts import get_object_or_404
from packages.models import Package


def bag_contents(request):
    """Context processor to include bag contents across the site."""
    bag_items = []
    total = 0
    package_count = 0
    bag = request.session.get('bag', {})

    # Iterate over the items in the session bag
    for item_id, quantity in bag.items():
        # Get the package object for each item
        package = get_object_or_404(Package, pk=item_id)
        total += quantity * package.price
        package_count += quantity
        # Append package and its quantity to the bag_items list
        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'package': package,
            'total_price': quantity * package.price,
        })

    context = {
        'bag_items': bag_items,
        'total': total,
        'package_count': package_count,
    }

    return context
