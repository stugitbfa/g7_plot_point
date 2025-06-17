from django.shortcuts import render

# Create your views here.
def login(request):
    return render(request, 'web/login.html')

def register(request):
    return render(request, 'web/register.html')

def forgot_password(request):
    return render(request, 'web/forgot_password.html')

def index(request):
    return render(request, 'web/index.html')

def services(request):
    return render(request, 'web/services.html')

def properties(request):
    return render(request, 'web/properties.html')

def property_single(request):
    return render(request, 'web/property-single.html')

def about(request):
    return render(request, 'web/about.html')

def contact(request):
    return render(request, 'web/contact.html')