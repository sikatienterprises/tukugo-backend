from django.urls import path
from .views import rate_ride, report_issue

urlpatterns = [
    path('ride/rate/', rate_ride),
    path('ride/report-issue/', report_issue),
]
