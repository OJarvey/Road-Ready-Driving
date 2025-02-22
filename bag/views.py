from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from packages.models import Package

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
    """ Add a quantity of the specified package to the bag """
    quantity = request.POST.get('quantity')

    # Validate quantity input
    if not quantity or not quantity.isdigit():
        return JsonResponse({'success': False, 'error': 'Invalid quantity. Please enter a number between 1 and 10.'}, status=400)

    quantity = int(quantity)

    # Ensure quantity is between 1 and 10
    if quantity < 1 or quantity > 10:
        return JsonResponse({'success': False, 'error': 'Quantity must be between 1 and 10.'}, status=400)

    redirect_url = request.POST.get('redirect_url', '/')
    bag = request.session.get('bag', {})

    if str(item_id) in bag:
        bag[str(item_id)] += quantity
    else:
        bag[str(item_id)] = quantity

    request.session['bag'] = bag
    return redirect(redirect_url)

def update_bag(request, item_id):
    try:
        quantity = int(request.POST.get("quantity", 1))
        bag = request.session.get('bag', {})
        item_id_str = str(item_id)
        
        package = Package.objects.get(id=item_id)
        
        if quantity > 0:
            bag[item_id_str] = quantity
        else:
            bag.pop(item_id_str, None)
            
        request.session['bag'] = bag
        
        # Convert Decimal to float for JSON serialization
        subtotal = float(package.price * quantity)
        grand_total = float(sum(
            Package.objects.get(id=int(k)).price * v 
            for k, v in bag.items()
        ))
        package_count = sum(bag.values())

        return JsonResponse({
            'success': True,
            'subtotal': subtotal,
            'grand_total': grand_total,
            'item_count': package_count,
            'message': 'Updated successfully'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def remove_from_bag(request, item_id):
    """ Remove a package from the bag """
    bag = request.session.get('bag', {})

    if str(item_id) in bag:
        del bag[str(item_id)]
        request.session['bag'] = bag  # Save changes to session

    total = sum(Package.objects.get(id=int(k)).price * v for k, v in bag.items()) if bag else 0
    package_count = sum(bag.values()) if bag else 0

    return JsonResponse({
        'success': True,
        'grand_total': total,
        'item_count': package_count,
        'message': 'Booking removed successfully!'
    })