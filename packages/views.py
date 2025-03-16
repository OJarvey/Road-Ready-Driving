from django.shortcuts import render, get_object_or_404, redirect
from .models import Package
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from .forms import PackageForm


def all_packages(request):
    """ A view to return the packages page """
    packages = Package.objects.all()
    query = None
    sort = request.GET.get('sort', '')
    
    # Handle searching
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

def add_package(request):
    """ Add a package to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES)
        if form.is_valid():
            package = form.save()
            messages.success(request, 'Successfully added package!')
            return redirect(reverse('package_detail', args=[package.id]))
        else:
            messages.error(request, 'Failed to add package. Please ensure the form is valid.')
    else:
        form = PackageForm()
    
    template = 'packages/add_package.html'
    context = {
        'form': form,
    }
    
    return render(request, template, context)
