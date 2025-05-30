from django.contrib import admin
from reviews.models import RideRating,RideIssue,DriverSupportRequest

admin.site.register(RideRating)
admin.site.register(RideIssue)
admin.site.register(DriverSupportRequest)

