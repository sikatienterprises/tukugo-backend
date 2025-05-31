from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Driver,RiderLocation,DriverPenalty
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
    
# penalty function after driver cancel ride book incress 1 point penalty
def cancel_and_reassign_ride(ride: Ride, cancelling_driver, reason):
    # 1. Mark ride cancelled
    ride.status = 'cancelled'
    ride.cancel_reason = reason
    ride.save()

    # 2. Log penalty
    DriverPenalty.objects.create(
        driver=cancelling_driver,
        ride=ride,
        reason=reason,
        penalty_points=1
    )

    # 3. Find another available driver
    new_driver = Driver.objects.filter(
        is_available=True,
        vehicle_type=ride.vehicle_type
    ).exclude(id=cancelling_driver.id).first()

    if new_driver:
        ride.driver = new_driver
        ride.status = 'reassigned'
        ride.save()

        # Send notification to new driver (placeholder)
        print(f"Ride {ride.id} reassigned to {new_driver.user.username}")

    else:
        print("No available drivers to reassign.")

#when driver cancel ride after assign ride
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancelled_ride(request):
    user = request.user
    driver = getattr(user, 'driver_profile', None)

    if not driver:
        return Response({"error": "Only drivers can cancel rides."}, status=403)

    ride_id = request.data.get('ride_id')
    reason = request.data.get('reason', '')

    try:
        ride = Ride.objects.get(id=ride_id, driver=driver)

        if ride.status != 'assigned':
            return Response({"error": "Only assigned rides can be cancelled."}, status=400)

        # Update ride status
        ride.status = 'cancelled'
        ride.save()

        # Log or store the cancellation reason (optional)
        # You can create a model like DriverPenalty
        cancel_and_reassign_ride(ride, cancelling_driver=driver, reason=reason)

        # Auto-reassign logic placeholder (implement based on your logic)
        # reassign_ride_to_another_driver(ride)

        return Response({
            "message": "Ride cancelled and reassigned if another driver is available.",
            "reassign_attempted": True,  # or False based on logic
        }, status=200)

    except Ride.DoesNotExist:
        return Response({"error": "Ride not found or not assigned to you."}, status=400)

#online offline available or not
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_driver_availability(request):
    try:
        driver = Driver.objects.get(user=request.user)
        if request.user.role != 'driver':
            return Response({"error": "Permission denied."}, status=403)

        # Flip the availability
        driver.is_available = not driver.is_available
        driver.save()

        return Response({
            "message": f"Driver is now {'Online' if driver.is_available else 'Offline'}",
            "is_available": driver.is_available
        }, status=status.HTTP_200_OK)

    except Driver.DoesNotExist:
        return Response({"error": "Driver profile not found."}, status=status.HTTP_404_NOT_FOUND)