from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q


from .models import *
from .helpers import *
from .forms import *

from functools import wraps
from django.utils import timezone

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
    properties = Property.objects.prefetch_related('images').select_related('address').all()[:9]
    total_properties = Property.objects.count()
    tenant_count = Customer.objects.filter(user_type='tenant').count()
    owner_count = Customer.objects.filter(user_type='owner').count()
    unique_city_count = Address.objects.values('city').distinct().count()
    context = {
        'properties': properties,
        'total_properties':total_properties,
        'tenant_count':tenant_count,
        'owner_count':owner_count,
        'unique_city_count':unique_city_count
    }
    return render(request, 'web/index.html', context)

def services(request):
    return render(request, 'web/services.html')


def properties(request):
    query = request.GET.get('q')
    
    property_list = Property.objects.prefetch_related('images').select_related('address')
    
    if query:
        property_list = property_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(property_type__icontains=query) |
            Q(address__city__icontains=query) |
            Q(address__state__icontains=query) |
            Q(address__pincode__icontains=query)
        )

    paginator = Paginator(property_list, 6)  # 6 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'properties': page_obj.object_list,
        'query': query,
    }
    return render(request, 'web/properties.html', context)


def owner_property(request):
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)

    property_instance = Property.objects.filter(owner=customer).first()
    address_instance = property_instance.address if property_instance and hasattr(property_instance, 'address') else None

    form = PropertyForm(instance=property_instance)
    address_form = AddressForm(instance=address_instance)
    image_form = PropertyImageForm()
    images = property_instance.images.all() if property_instance else []

    if request.method == 'POST':
        if 'submit_property' in request.POST:
            form = PropertyForm(request.POST, instance=property_instance)
            address_form = AddressForm(request.POST, instance=address_instance)

            if form.is_valid() and address_form.is_valid():
                property_obj = form.save(commit=False)
                property_obj.owner = customer
                property_obj.save()

                address_obj = address_form.save(commit=False)
                address_obj.property = property_obj
                address_obj.save()

                return redirect('property_single')

        elif 'submit_image' in request.POST:
            image_form = PropertyImageForm(request.POST, request.FILES)
            if image_form.is_valid() and property_instance:
                image = image_form.save(commit=False)
                image.property = property_instance
                image.save()
                return redirect('property_single')

    context = {
        'customer': customer,
        'form': form,
        'address_form': address_form,
        'image_form': image_form,
        'is_edit': property_instance is not None,
        'property': property_instance,
        'images': images,
    }

    return render(request, 'web/owner_property.html', context)

@login_required
def property_detail(request, pk):
    property_obj = get_object_or_404(Property.objects.select_related('owner', 'address').prefetch_related('images'), pk=pk)

    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)

    context = {
        'property': property_obj,
        'owner': property_obj.owner,
        'address': property_obj.address,
        'images': property_obj.images.all(),
        'customer':customer
    }
    return render(request, 'web/property-single.html', context)

@login_required
def send_booking_request(request, id):
    property = get_object_or_404(Property, id=id)

    # Get full Customer object from session
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, "Customer session not found.")
        return redirect('property_detail', pk=id)


    customer = get_object_or_404(Customer, id=customer_id)

    # Only tenant can book
    if customer.user_type != 'tenant':
        messages.warning(request, "Only tenants can send booking requests.")
        return redirect('property_detail', pk=id)


    # Check if already requested
    existing = Booking.objects.filter(property=property, tenant=customer, status='pending')
    if existing.exists():
        messages.info(request, "You have already requested booking for this property.")
        return redirect('property_detail', pk=id)


    # Create booking
    Booking.objects.create(
        tenant=customer,
        property=property,
        start_date=timezone.now().date(),
        status='pending'
    )
    messages.success(request, "Booking request sent successfully!")
    return redirect('property_detail', pk=id)



@login_required
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Make sure only the owner of the property can update
    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, id=customer_id)

    if booking.property.owner != customer:
        messages.error(request, "You are not authorized to update this booking.")
        return redirect('profile')

    new_status = request.POST.get('status')
    if new_status in dict(Booking._meta.get_field('status').choices).keys():
        booking.status = new_status
        booking.save()
        messages.success(request, "Booking status updated successfully.")
    else:
        messages.error(request, "Invalid status.")

    return redirect('profile')



def about(request):
    return render(request, 'web/about.html')


def contact(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for contacting us. We will reply soon.")
            return redirect('contact')
    context = {
        'form':form
    }
    return render(request, 'web/contact.html', context)

@login_required
def profile(request):
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)

    tenant_bookings = Booking.objects.filter(tenant=customer) if customer.user_type == 'tenant' else None
    owner_bookings = Booking.objects.filter(property__owner=customer) if customer.user_type == 'owner' else None

    context = {
        'customer': customer,
        'tenant_bookings':tenant_bookings,
        'owner_bookings':owner_bookings
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