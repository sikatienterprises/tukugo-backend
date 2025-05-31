from django.contrib import admin
from driver.models import Driver,RiderLocation,DriverPenalty

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'license_number', 'vehicle_type', 'created_at','is_available']
    search_fields = ['user__username', 'license_number', 'vehicle_type','is_available']
    list_filter = ['vehicle_type', 'created_at']
    ordering = ['-created_at']


admin.site.register(RiderLocation)
admin.site.register(DriverPenalty)