from django.urls import path
from .views import *


urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('email_verify/', email_verify, name='email_verify'),

    path('', index, name='index'),
    path('services/', services, name='services'),
    path('properties/', properties, name='properties'),
    path('property/<uuid:pk>/', property_detail, name='property_detail'),
    path('owner_property/', owner_property, name='owner_property'),
    path('property/<uuid:id>/book/', send_booking_request, name='send_booking_request'),
    path('booking/<uuid:booking_id>/status/', update_booking_status, name='update_booking_status'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('profile/', profile, name='profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('logout/', logout, name='logout')

]