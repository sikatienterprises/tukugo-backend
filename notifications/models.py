from django.db import models
from django.conf import settings
from driver.models import Driver

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Target audience
    send_to_all = models.BooleanField(default=False)
    send_to_customers = models.BooleanField(default=False)
    send_to_drivers = models.BooleanField(default=False)

    # Optional targeting
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    target_driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True)
    vehicle_type = models.CharField(max_length=20, blank=True, null=True)  # bike, car, auto, etc.

    def __str__(self):
        return self.title
