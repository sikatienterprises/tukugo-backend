from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Driver,RiderLocation
from customer.models import Ride
from .serializers import DriverSerializer,RiderLocationSerializer,RideListSerializer,AcceptRideSerializer
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class DriverListCreateView(generics.ListCreateAPIView):
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Driver.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": True,
            "message": "Driver data fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        if request.user.role != 'driver':
            return Response({
                "status": False,
                "message": "Only users with the 'driver' role can create driver profiles"
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({
            "status": True,
            "message": "Driver created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

class DriverDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Driver.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "status": True,
            "message": "Driver details retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        if request.user.role != 'driver':
            return Response({
                "status": False,
                "message": "Only users with the 'driver' role can update driver data"
            }, status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "status": True,
            "message": "Driver updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": True,
            "message": "Driver deleted successfully",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)


#for rider location
class UpdateLocationAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.role != 'driver':
            return Response({
                "status": False,
                "message": "Only users with the 'driver' role can create driver profiles"
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = RiderLocationSerializer(data=request.data)
        if serializer.is_valid():
            location, created = RiderLocation.objects.update_or_create(
                user=request.user,
                defaults={
                    'latitude': serializer.validated_data['latitude'],
                    'longitude': serializer.validated_data['longitude'],
                }
            )
            return Response({'message': 'Location updated successfully'}, status=200)
        return Response(serializer.errors, status=400)
    


#ride view,accept and set price

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_rides(request):
    driver = request.user.driver_profile
    rides = Ride.objects.filter(status='requested', vehicle_type=driver.vehicle_type)
    serializer = RideListSerializer(rides, many=True)
    return Response(serializer.data)

#customer assign this ride and set the price
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_ride(request):
    serializer = AcceptRideSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    ride_id = serializer.validated_data['ride_id']
    fare = serializer.validated_data['fare']

    try:
        ride = Ride.objects.get(id=ride_id, status='requested')
    except Ride.DoesNotExist:
        return Response({'error': 'Ride not available or already assigned.'}, status=404)

    driver = request.user.driver_profile
    ride.driver = driver
    ride.status = 'assigned'
    ride.fare = fare
    ride.save()

    return Response({
        "message": "Ride accepted.",
        "ride_id": ride.id,
        "status": ride.status,
        "fare": str(ride.fare)
    })

#Updates the ride status from assigned → ongoing

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_ride(request):
    driver = request.user.driver_profile
    ride_id = request.data.get('ride_id')

    try:
        ride = Ride.objects.get(id=ride_id, driver=driver, status='assigned')
        ride.status = 'ongoing'
        ride.save()
        return Response({"message": "Ride started successfully."}, status=200)
    except Ride.DoesNotExist:
        return Response({"error": "Ride not found or not in 'assigned' status."}, status=400)



#Updates the ride status from ongoing ->complete

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_ride(request):
    driver = request.user.driver_profile
    ride_id = request.data.get('ride_id')

    try:
        ride = Ride.objects.get(id=ride_id, driver=driver, status='ongoing')
        ride.status = 'completed'
        ride.save()
        return Response({"message": "Ride complete successfully."}, status=200)
    except Ride.DoesNotExist:
        return Response({"error": "Ride not found or not in 'ongoing' status."}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancelled_ride(request):
    driver = request.user.driver_profile
    ride_id = request.data.get('ride_id')

    try:
        ride = Ride.objects.get(id=ride_id, driver=driver)
        ride.status = 'cancelled'
        ride.save()
        return Response({"message": "Ride cancelled successfully."}, status=200)
    except Ride.DoesNotExist:
        return Response({"error": "Ride not found "}, status=400)
