from django.shortcuts import render, get_object_or_404, redirect
from .models import Package
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q


def all_packages(request):
    """ A view to return the packages page """
    packages = Package.objects.all()
    query = None
    
    if request.GET:
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('packages'))
            
            query = Q(name__icontains=query) | Q(description__icontains=query)
            packages = packages.filter(query)
    
    context = {
        'packages': packages,
        'search_term': query,
    }
    
    return render(request, 'packages/packages.html', context)

def package_detail(request, package_id):
    """ A view to return the package detail page """
    package = get_object_or_404(Package, pk=package_id)
    
    context = {
        'package': package,
    }
    
    return render(request, 'packages/packages_detail.html', context)

