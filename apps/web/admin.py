from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'mobile', 'user_type', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'mobile')
    list_filter = ('user_type', 'is_active')


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'rent_amount', 'is_available', 'property_type')
    search_fields = ('title',)
    list_filter = ('is_available', 'property_type')
    autocomplete_fields = ['owner']


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'caption')
    search_fields = ('property__title',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('property', 'street', 'city', 'state', 'pincode')
    search_fields = ('city', 'state', 'pincode')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('property', 'tenant', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date')
    search_fields = ('property__title', 'tenant__first_name', 'tenant__last_name')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'create_at')
    list_filter = ('status', 'create_at')
    search_fields = ('name', 'email', 'subject')
