from django.contrib import messages
from packages.models import Package
from decimal import Decimal


def bag_contents(request):
    """Context processor to include bag contents across the site."""
    bag_items = []
    total = Decimal("0.00")
    package_count = 0
    bag = request.session.get("bag", {})
    invalid_items = []

    # Iterate over the items in the session bag
    for item_id, quantity in bag.items():
        try:
            package = Package.objects.get(pk=item_id)
            total += quantity * package.price
            package_count += quantity
            # Append package and its quantity to the bag_items list
            bag_items.append(
                {
                    "item_id": item_id,
                    "quantity": quantity,
                    "package": package,
                    "total_price": quantity * package.price,
                }
            )
        except Package.DoesNotExist:
            invalid_items.append(item_id)
            messages.error(
                request, 
                f"A package in your bag is no longer available"
            )

    # Remove invalid items from the bag
    for item_id in invalid_items:
        del bag[item_id]

    if invalid_items:
        request.session["bag"] = bag
        messages.error(
            request, 
            "Some unavailable items were removed from your bag"
        )

    # Calculate processing fee (Takes 0.01% of total)
    processing_fee = total * Decimal("0.01")
    grand_total = total + processing_fee

    context = {
        "bag_items": bag_items,
        "total": total,
        "processing_fee": processing_fee,
        "grand_total": grand_total,
        "package_count": package_count,
    }

    return context
