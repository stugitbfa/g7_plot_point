from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages

from .models import *
from .helpers import *

from functools import wraps
import random


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'customer_id' not in request.session:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper 

def login(request):
    if request.method == 'POST':
        email_ = request.POST['email']
        password_ = request.POST['password']

        if not Customer.objects.filter(email=email_).exists():
            messages.error(request, "Email doesn't exist.")
            return redirect('login')

        get_customer = Customer.objects.get(email=email_)

        if not get_customer.is_active:
            messages.warning(request, "Your account is deactivated. Please contact support.")
            return redirect('login')

        is_valid = check_password(password_, get_customer.password)
        if not is_valid:
            messages.error(request, "Email or password doesn't match.")
            return redirect('login')

        request.session['customer_id'] = str(get_customer.id)
        messages.success(request, "Login successful.")
        return redirect('index')

    return render(request, 'web/login.html')

def register(request):
    if request.method == 'POST':
        user_type_ = request.POST['user_type']
        firstname_ = request.POST['firstname']
        lastname_ = request.POST['lastname']
        email_ = request.POST['email']
        mobile_ = request.POST['mobile']
        password_ = request.POST['password']
        confirm_password_ = request.POST['confirm_password']

        if not is_email_verified(email_):
            messages.error(request, "Invalid email address.")
            return redirect('register')

        if Customer.objects.filter(email=email_).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        if not is_valid_mobile_number(mobile_):
            messages.error(request, "Invalid mobile number.")
            return redirect('register')

        if password_ != confirm_password_:
            messages.error(request, "Password and confirm password do not match.")
            return redirect('register')
        


        if not validate_password(password_)[0]:
            messages.error(request, validate_password(password_)[1])
            return redirect('register')

        new_customer = Customer.objects.create(
            user_type=user_type_,
            first_name=firstname_,
            last_name=lastname_,
            email=email_,
            mobile=mobile_,
            password=make_password(password_)
        )

        otp = random.randint(111111, 999999)
        new_customer.otp = otp
        new_customer.save()

        subject = "Confirm Your Account | PLOT-POINT"
        message = f"""
        Dear User,

        Thank you for registering with PLOT-POINT.

        Your One-Time Password (OTP) for email verification is: {otp}

        Please enter this OTP in the app/website to complete your email verification process. 

        If you did not request this, please ignore this email.

        Best regards,  
        Team PLOT-POINT
        """
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email_])

        messages.success(request, "Registration successful! Please check your email for OTP verification.")
        return render(request, 'web/email_verify.html', {'email': email_})

    return render(request, 'web/register.html')

def email_verify(request):
    if request.method == 'POST':
        email_ = request.POST['email']
        otp_ = request.POST['otp']

        if not Customer.objects.filter(email=email_).exists():
            messages.error(request, "Email does not exist.")
            return render(request, 'web/email_verify.html', {'email': email_})

        get_customer = Customer.objects.get(email=email_)

        if otp_ != get_customer.otp:
            messages.error(request, "Invalid OTP.")
            return render(request, 'web/email_verify.html', {'email': email_})

        get_customer.is_active = True
        get_customer.save()

        messages.success(request, "Email verified successfully. You can now login.")
        return redirect('login')

    return render(request, 'web/email_verify.html')


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

@login_required
def profile(request):
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    context = {
        'customer':customer
    }
    return render(request, 'web/profile.html', context)

@login_required
def edit_profile(request):
    customer_id = request.session.get('customer_id')
   
    customer = Customer.objects.get(id=customer_id)

    if request.method == 'POST':
        customer.first_name = request.POST.get('first_name')
        customer.last_name = request.POST.get('last_name')
        customer.email = request.POST.get('email')
        customer.mobile = request.POST.get('mobile')
        customer.save()
        messages.success(request, "Profile updated successfully")
        return redirect('profile')

    return render(request, 'web/edit_profile.html', {'customer': customer})

@login_required
def logout(request):
    del request.session['customer_id']
    messages.success(request, 'Now, you are logged Out.')
    return redirect('login')