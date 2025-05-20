from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('custom_auth.urls')),
    path('api/customer/', include('customer.urls')),
    path('api/driver/', include('driver.urls')),
    path('api/review/', include('reviews.urls')),
    path('api/notifications/', include('notifications.urls')),


]
