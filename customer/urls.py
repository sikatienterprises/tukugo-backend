from django.urls import path
from .views import CustomerListCreateView, CustomerDetailView,RideRequestAPIView,RideEstimateAPIView,RideOptionsAPIView,RideCancelAPIView,RideStatusAPIView,CaptainDetailsAPIView
from .views import ride_history,ride_invoice

urlpatterns = [
    path('', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('ride/request/', RideRequestAPIView.as_view(), name='ride-request'),
    #http://localhost:8000/api/customer/ride/estimate?pickup_lat=12.9716&pickup_lng=77.5946&drop_lat=12.9763&drop_lng=77.6034&vehicle_type=bike
    path('ride/estimate/', RideEstimateAPIView.as_view(), name='ride-estimate'),
    path('ride/options/', RideOptionsAPIView.as_view(), name='ride-options'),
    path('ride/cancel/', RideCancelAPIView.as_view(), name='ride-cancel'),
    path('ride/status', RideStatusAPIView.as_view(), name='ride-status'),
    path('ride/captain-details', CaptainDetailsAPIView.as_view(), name='ride-captain-details'),
    #history of rides and invoice
    path('rides/history', ride_history),
    path('rides/<int:ride_id>/invoice', ride_invoice),

]
