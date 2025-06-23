from django.urls import path
from .views import *


urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('email_verify/', email_verify, name='email_verify'),

    path('', index, name='index'),
    path('services/', services, name='services'),
    path('properties/', properties, name='properties'),
    path('property-single/', property_single, name='property_single'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('profile/', profile, name='profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('logout/', logout, name='logout')

]