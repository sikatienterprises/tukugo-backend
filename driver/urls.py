from django.urls import path
from driver.views import DriverListCreateView, DriverDetailView,UpdateLocationAPIView,available_rides, accept_ride,start_ride,complete_ride,cancelled_ride,toggle_driver_availability

urlpatterns = [
    path('', DriverListCreateView.as_view(), name='driver-list-create'),
    path('<int:pk>/', DriverDetailView.as_view(), name='driver-detail'),
    path('loction_update/', UpdateLocationAPIView.as_view(), name='update-location'),
    path('rides/available/', available_rides),   # GET show available rids in a list
    path('rides/accept/', accept_ride),          # POST changes status to assigned
    path('rides/start/', start_ride), # POST change status on ongoing
    path('rides/complete/', complete_ride), # POST change status on complete
    path('rides/cancelled/', cancelled_ride), # POST change status on cancel
    path('toggle-availability/', toggle_driver_availability, name='toggle-availability'), #change onine-offline and offline to online



]


