from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import RideRatingSerializer, RideIssueSerializer,DriverSupportRequestSerializer

from customer.models import Ride  
from reviews.models import RideRating  ,RideIssue

#this is for give rating if ride was complted
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_ride(request):
    ride_id = request.data.get('ride')
    if not ride_id:
        return Response({"error": "Ride ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        ride = Ride.objects.get(id=ride_id, customer=request.user)
    except Ride.DoesNotExist:
        return Response({"error": "Ride not found or you are not authorized"}, status=status.HTTP_404_NOT_FOUND)
    
    if ride.status != 'completed':
        return Response({"error": "Cannot rate a ride before it is completed"}, status=status.HTTP_400_BAD_REQUEST)

    # Check if already rated
    if RideRating.objects.filter(ride=ride, customer=request.user).exists():
        return Response({"error": "You have already rated this ride"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = RideRatingSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Rating submitted successfully"}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_issue(request):
    ride_id = request.data.get('ride')
    if not ride_id:
        return Response({"error": "Ride ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        ride = Ride.objects.get(id=ride_id, customer=request.user)
    except Ride.DoesNotExist:
        return Response({"error": "Ride not found or you are not authorized"}, status=status.HTTP_404_NOT_FOUND)
    
        # Check if already report
    if RideIssue.objects.filter(ride=ride, customer=request.user).exists():
        return Response({"error": "You have already report this ride"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = RideIssueSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Issue reported successfully"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#view only his own feedback which given from users
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def driver_reviews(request):
    if request.user.role != 'driver':
        return Response({"error": "Permission denied."}, status=403)

    driver = request.user.driver_profile
    ratings = RideRating.objects.filter(driver=driver).order_by('-created_at')
    serializer = RideRatingSerializer(ratings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def raise_driver_support_request(request):
    if request.user.role != 'driver':
        return Response({"error": "Permission denied."}, status=403)

    driver = request.user.driver_profile
    serializer = DriverSupportRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(driver=driver)
        return Response({"message": "Support request submitted successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)