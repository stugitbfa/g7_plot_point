from django.urls import path
from .views import *


urlpatterns = [
    path('', login, name='login'),
    path('register/', register, name='register'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('index/', index, name='index'),
    path('services/', services, name='services'),
    path('properties/', properties, name='properties'),
    path('property-single/', property_single, name='property_single'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),

]