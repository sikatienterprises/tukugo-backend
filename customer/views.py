from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Customer,Ride
from .serializers import CustomerSerializer,RideRequestSerializer,CaptainDetailsSerializer
from rest_framework.views import APIView

from .serializers import RideSerializer  # Make sure this exists
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit  # You can use xhtml2pdf or weasyprint as alternatives
from django.shortcuts import get_object_or_404

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class CustomerListCreateView(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if request.user.role != 'customer':
            return Response({
                "status": False,
                "message": "Only users with 'customer' role can create customer profiles"
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({
            "status": True,
            "message": "Customer created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Customer.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "status": True,
            "message": "Customer details retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        if request.user.role != 'customer':
            return Response({
                "status": False,
                "message": "Only users with 'customer' role can update customer data"
            }, status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "status": True,
            "message": "Customer updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)



    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": True,
            "message": "Customer deleted successfully",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)


#ride booking 
from django.utils.timezone import now
from math import radians, cos, sin, sqrt, atan2
# Helper function to calculate ETA and fare
def calculate_eta_and_fare(pickup_lat, pickup_lng, drop_lat, drop_lng, vehicle_type):
    R = 6371  # Earth radius in km
    lat1 = radians(pickup_lat)
    lon1 = radians(pickup_lng)
    lat2 = radians(drop_lat)
    lon2 = radians(drop_lng)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c  # in kilometers

    base_fare = 20
    per_km_rate = {
        'bike': 5,
        'auto': 8,
        'car': 12,
        'truck': 20,
        'loading': 25
    }

    fare = base_fare + distance * per_km_rate.get(vehicle_type, 10)
    eta = int(distance / 0.5)  # assume average speed 30km/h => 0.5km/min

    return round(fare, 2), eta


class RideRequestAPIView(APIView):
    def post(self, request):
        serializer = RideRequestSerializer(data=request.data)
        if serializer.is_valid():
            ride = serializer.save(customer=request.user)
            return Response({"message": "Ride requested successfully", "ride_id": ride.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RideEstimateAPIView(APIView):
    def get(self, request):
        try:
            pickup_lat = float(request.query_params.get("pickup_lat"))
            pickup_lng = float(request.query_params.get("pickup_lng"))
            drop_lat = float(request.query_params.get("drop_lat"))
            drop_lng = float(request.query_params.get("drop_lng"))
            vehicle_type = request.query_params.get("vehicle_type")

            fare, eta = calculate_eta_and_fare(pickup_lat, pickup_lng, drop_lat, drop_lng, vehicle_type)

            return Response({"estimated_fare": fare, "eta_minutes": eta})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RideOptionsAPIView(APIView):
    def get(self, request):
        options = dict(Ride._meta.get_field('vehicle_type').choices)
        return Response({"vehicle_options": options})


class RideCancelAPIView(APIView):
    def post(self, request):
        ride_id = request.data.get("ride_id")
        try:
            ride = Ride.objects.get(id=ride_id, customer=request.user)
            ride.delete()
            return Response({"message": "Ride cancelled successfully."})
        except Ride.DoesNotExist:
            return Response({"error": "Ride not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

#ride status
class RideStatusAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ride = Ride.objects.filter(customer=request.user).order_by('-requested_at').first()
        if not ride:
            return Response({'detail': 'No active ride found'}, status=404)
        
        return Response({
            'ride_id': ride.id,
            'status': ride.status,
            'vehicle_type': ride.vehicle_type,
            'pickup': ride.pickup_location,
            'drop': ride.drop_location,
        })
    

# driver's info who acceptd
class CaptainDetailsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ride = Ride.objects.filter(customer=request.user, driver__isnull=False).order_by('-requested_at').first()
        if not ride:
            return Response({'detail': 'No assigned driver found.'}, status=404)
        
        serializer = CaptainDetailsSerializer(ride)
        return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ride_history(request):
    user = request.user
    if user.role != 'customer':
        return Response({"detail": "Only customers can access ride history."}, status=status.HTTP_403_FORBIDDEN)
    
    rides = Ride.objects.filter(customer=user, status='completed').order_by('-requested_at')
    serializer = RideSerializer(rides, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ride_invoice(request, ride_id):
    user = request.user
    ride = get_object_or_404(Ride, id=ride_id, customer=user)

    html_content = render_to_string('invoice_template.html', {'ride': ride})
    return HttpResponse(html_content)


#for invoice
from django.shortcuts import get_object_or_404, render
from .models import Ride

def download_invoice(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, customer=request.user)
    return render(request, 'invoice_template.html', {'ride': ride})

