from django.shortcuts import render, get_object_or_404, redirect
from .models import Package
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q, ProtectedError
from .forms import PackageForm
from django.contrib.auth.decorators import login_required


def all_packages(request):
    """A view to return the packages page"""
    packages = Package.objects.all()
    query = None
    sort = request.GET.get("sort", "")

    # Sorting functionality
    if sort:
        sort_key = sort
        if sort == "price_asc":
            sort_key = "price"
        elif sort == "price_desc":
            sort_key = "-price"
        elif sort == "name_asc":
            sort_key = "name"
        elif sort == "name_desc":
            sort_key = "-name"
        packages = packages.order_by(sort_key)

    # Search functionality
    if request.GET:
        if "q" in request.GET:
            query = request.GET["q"]
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse("packages"))

            query = Q(name__icontains=query) | Q(description__icontains=query)
            packages = packages.filter(query)

    context = {
        "packages": packages,
        "search_term": query,
        "current_sorting": sort,
    }

    return render(request, "packages/packages.html", context)


def package_detail(request, package_id):
    """A view to return the package detail page"""
    package = get_object_or_404(Package, pk=package_id)

    context = {
        "package": package,
    }

    return render(request, "packages/packages_detail.html", context)


@login_required
def add_package(request):
    """Add a package to the store"""
    if not request.user.is_superuser:
        messages.error(request, "Sorry, only store owners can do that.")
        return redirect(reverse("home"))

    if request.method == "POST":
        form = PackageForm(request.POST, request.FILES)
        if form.is_valid():
            package = form.save()
            messages.success(request, "Successfully added package!")
            return redirect(reverse("package_detail", args=[package.id]))
        else:
            messages.error(
                request, "Failed to add package. Please ensure the form is valid."
            )
    else:
        form = PackageForm()

    template = "packages/add_package.html"
    context = {
        "form": form,
    }

    return render(request, template, context)


@login_required
def edit_package(request, package_id):
    """Edit an existing package"""
    if not request.user.is_superuser:
        messages.error(request, "Sorry, only store owners can do that.")
        return redirect(reverse("home"))

    package = get_object_or_404(Package, pk=package_id)
    if request.method == "POST":
        form = PackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Successfully updated package!")
                return redirect(reverse("package_detail", args=[package.id]))
            except Exception as e:
                messages.error(request, f"Failed to update package: {str(e)}")
        else:
            messages.error(
                request, "Failed to update package. Please ensure the form is valid."
            )
    else:
        form = PackageForm(instance=package)

    template = "packages/edit_package.html"
    context = {
        "form": form,
        "package": package,
    }

    return render(request, template, context)


@login_required
def delete_package(request, package_id):
    """Delete a package from the store"""
    if not request.user.is_superuser:
        messages.error(request, "Sorry, only store owners can do that.")
        return redirect(reverse("home"))

    package = get_object_or_404(Package, pk=package_id)

    if request.method == "POST":
        try:
            # Remove package from all bags
            bag = request.session.get("bag", {})
            if str(package.id) in bag:
                del bag[str(package.id)]
                request.session["bag"] = bag

            package.delete()
            messages.success(request, "Package deleted successfully!")
            return redirect("packages")
        except ProtectedError as e:
            messages.error(
                request, f"Cannot delete {package.name} - it exists in order history."
            )
            return redirect("packages")

    context = {"package": package}
    return render(request, "packages/delete_package.html", context)
