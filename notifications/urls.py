from django.urls import path
from .views import send_notification, notification_list

urlpatterns = [
    path('admin/send/', send_notification),   # only for Admin send API
    path('show/', notification_list),         # Customer/Driver view notification API
]
