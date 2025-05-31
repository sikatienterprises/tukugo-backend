from django.db import models
from custom_auth.models import User
from django.conf import settings

class Driver(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('bike', 'Bike Taxi'),
        ('auto', 'Auto Rickshaw'),
        ('car', 'Car'),
        ('truck', 'Truck'),
        ('loading', 'Loading Vehicle'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    vehicle_number = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_available else 'Offline'}"

#for rider's location
class RiderLocation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - ({self.latitude}, {self.longitude})"
    


class DriverPenalty(models.Model):
    driver = models.ForeignKey('driver.Driver', on_delete=models.CASCADE)
    ride = models.ForeignKey('customer.Ride', on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    penalty_points = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)