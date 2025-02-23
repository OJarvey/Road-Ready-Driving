from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from packages.models import Package
from django.contrib import messages
from django.urls import reverse

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
        'packages_url': reverse('packages'),
    }

    return render(request, 'bag/bag.html', context)

def add_to_bag(request, item_id):
    """ Add a quantity of the specified package to the bag """
    quantity = request.POST.get('quantity')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # Validate quantity input
    if not quantity or not quantity.isdigit():
        error_message = "Invalid quantity. Please enter a number between 1 and 10."
        if is_ajax:
            return JsonResponse({'success': False, 'error': error_message}, status=400)
        messages.error(request, error_message)
        return redirect('view_bag')

    quantity = int(quantity)

    # Ensure quantity is between 1 and 10
    if quantity < 1 or quantity > 10:
        error_message = "You can only add up to 10 per item."
        if is_ajax:
            return JsonResponse({'success': False, 'error': error_message}, status=400)
        messages.error(request, error_message)
        return redirect('view_bag')

    redirect_url = request.POST.get('redirect_url', '/')
    bag = request.session.get('bag', {})
    package = get_object_or_404(Package, pk=item_id)
    item_id_str = str(item_id)

    if item_id_str in bag:
        if bag[item_id_str] + quantity > 10:
            error_message = f"Total quantity for {package.name} cannot exceed 10."
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_message}, status=400)
            messages.error(request, error_message)
            return redirect('view_bag')
        bag[item_id_str] += quantity
    else:
        bag[item_id_str] = quantity

    request.session['bag'] = bag
    success_message = f"Added {package.name} to your bag"

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': success_message,
            'item_count': sum(bag.values())
        })
    messages.success(request, success_message)
    return redirect(redirect_url)

def update_bag(request, item_id):
    """ Update the quantity of a package in the bag """
    try:
        quantity = int(request.POST.get("quantity", 1))
        bag = request.session.get('bag', {})
        item_id_str = str(item_id)
        package = get_object_or_404(Package, pk=item_id)

        if quantity > 10:
            return JsonResponse({
                'success': False,
                'error': f"Quantity for {package.name} cannot exceed 10."
            }, status=400)

        if quantity > 0:
            bag[item_id_str] = quantity
            success_message = f"Updated {package.name} quantity to {quantity}"
        else:
            bag.pop(item_id_str, None)
            success_message = f"Removed {package.name} from your bag"

        request.session['bag'] = bag
        
        subtotal = float(package.price * quantity) if quantity > 0 else 0
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
            'message': success_message
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def remove_from_bag(request, item_id):
    """ Remove a package from the bag """
    bag = request.session.get('bag', {})
    package = get_object_or_404(Package, pk=item_id)
    item_id_str = str(item_id)

    if item_id_str in bag:
        del bag[item_id_str]
        request.session['bag'] = bag
        success_message = f"Removed {package.name} from your bag"
    else:
        return JsonResponse({
            'success': False,
            'error': f"{package.name} not found in bag"
        }, status=400)

    total = float(sum(Package.objects.get(id=int(k)).price * v for k, v in bag.items())) if bag else 0
    package_count = sum(bag.values()) if bag else 0

    return JsonResponse({
        'success': True,
        'grand_total': total,
        'item_count': package_count,
        'message': success_message
    })