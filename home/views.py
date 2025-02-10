from django.shortcuts import render

def index(request):
    """ A view to return the index page """
    
    return render(request, 'home/index.html')

def about(request):
    return render(request, 'includes/about.html')

def about(request):
    return render(request, 'includes/contact.html')