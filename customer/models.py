from django.db import models
from custom_auth.models import User
from django.conf import settings
#customer personal data
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    


#booking information
class Ride(models.Model):
    VEHICLE_CHOICES = [
        ('bike', 'Bike Taxi'),
        ('auto', 'Auto Rickshaw'),
        ('car', 'Car'),
        ('truck', 'Truck'),
        ('loading', 'Loading Vehicle'),
    ]
    STATUS_CHOICES = [
    ('requested', 'Requested'),
    ('assigned', 'Assigned'),
    ('ongoing', 'Ongoing'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('reassigned', 'Reassigned'),
]


    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    pickup_location = models.CharField(max_length=255)
    drop_location = models.CharField(max_length=255)

    pickup_lat = models.FloatField()
    pickup_lng = models.FloatField()
    drop_lat = models.FloatField()
    drop_lng = models.FloatField()

    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES)

    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested') #create by default ,modify by driver
    driver = models.ForeignKey('driver.Driver', on_delete=models.SET_NULL, null=True, blank=True)
    cancel_reason = models.TextField(blank=True, null=True)
    fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # price of payment only set by driver only for now

    def __str__(self):
        return f"{self.customer} - {self.vehicle_type} from {self.pickup_location} to {self.drop_location}"
