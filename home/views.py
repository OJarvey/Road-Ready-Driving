from django.shortcuts import render

def index(request):
    """ A view to return the index page """
    
    return render(request, 'home/index.html')

def about(request):
    """A view to render the about page"""
    return render(request, 'includes/about.html')

def contact(request):
    """A view to render the contact page"""
    return render(request, 'includes/contact.html')