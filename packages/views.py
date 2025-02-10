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

