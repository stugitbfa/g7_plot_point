from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'mobile', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('first_name', 'last_name', 'email', 'mobile')
   


