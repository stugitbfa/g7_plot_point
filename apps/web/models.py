from django.db import models

import uuid
# Create your models here.

class BaseClass(models.Model):
    id = models.UUIDField(primary_key=True, blank=False, null=False, default=uuid.uuid4)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class Customer(BaseClass):
    USER_TYPE_CHOICES = [
        ('owner', 'Owner'),
        ('tenant', 'Tenant'),
    ]
    first_name = models.CharField(max_length=255, blank=True, default='-')
    last_name = models.CharField(max_length=255, blank=True, default='-')
    email = models.EmailField(max_length=255, unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    otp = models.CharField(max_length=20, default="112233")
    is_active = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='tenant')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Property(BaseClass):
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    area_sqft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    property_type = models.CharField(max_length=100, default='Flat')  # Flat, Villa, PG, etc.

    def __str__(self):
        return self.title
    
class PropertyImage(BaseClass):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.property.title}"


class Address(BaseClass):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='address')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.street}, {self.city}"
    

class Booking(BaseClass):
    tenant = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ], default='pending')

    def __str__(self):
        return f"{self.tenant} - {self.property}"
    
class Review(BaseClass):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1 to 5
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Review for {self.booking.property.title}"

    

class Payment(BaseClass):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_mode = models.CharField(max_length=50, default='online')  # online, cash, cheque, etc.
    status = models.CharField(max_length=50, choices=[
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ], default='pending')

    def __str__(self):
        return f"{self.booking} - {self.amount}"
