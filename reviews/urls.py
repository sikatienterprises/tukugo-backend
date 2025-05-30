from django.urls import path
from reviews.views import rate_ride, report_issue,driver_reviews,raise_driver_support_request

urlpatterns = [
    path('ride/rate/', rate_ride),
    path('ride/report-issue/', report_issue),
    path('driver/reviews/', driver_reviews, name='driver-reviews'),
    path('driver/support/', raise_driver_support_request, name='driver-support-request'),
]
