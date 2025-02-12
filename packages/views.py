from django.shortcuts import render
from .models import Package

# Create your views here.
from django.shortcuts import render

def all_packages(request):
    """ A view to return the packages page """
    packages = Package.objects.all()
    
    context = {
        'packages': packages,
    }
    
    return render(request, 'packages/packages.html', context)

def package_detail(request, package_id):
    """ A view to return the package detail page """
    package = Package.objects.get(id=package_id)
    
    context = {
        'package': package,
    }
    
    return render(request, 'packages/packages_detail.html', context)

