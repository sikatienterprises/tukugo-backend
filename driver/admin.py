from django.contrib import admin
from .models import Driver,RiderLocation

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'license_number', 'vehicle_type', 'created_at']
    search_fields = ['user__username', 'license_number', 'vehicle_type']
    list_filter = ['vehicle_type', 'created_at']
    ordering = ['-created_at']


admin.site.register(RiderLocation)