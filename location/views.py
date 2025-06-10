# views.py
import socket
import geocoder
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserLocation
from django.shortcuts import render

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_or_update_user_location(request):
#     user = request.user

#     # Get local IP address
#     hostname = socket.gethostname()
#     ip_address = socket.gethostbyname(hostname)

#     # Get location from IP
#     g = geocoder.ip('me')
#     if g.ok and g.latlng:
#         latitude, longitude = g.latlng
#     else:
#         return Response({'error': 'Could not detect location'}, status=400)

#     # Create or update location record
#     location, created = UserLocation.objects.update_or_create(
#         user=user,
#         defaults={
#             'ip_address': ip_address,
#             'latitude': latitude,
#             'longitude': longitude
#         }
#     )

#     return Response({
#         'message': 'Location saved' if created else 'Location updated',
#         'latitude': latitude,
#         'longitude': longitude,
#     })

# Render template
def map_page(request):
    return render(request, 'location_map.html')

def show_map(request):
    return render(request, "map.html")

# API to store location
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_location(request):
    user = request.user
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    lat = request.data.get('latitude')
    lng = request.data.get('longitude')

    # Save this in your model (e.g., DriverLocation)
    location, created = UserLocation.objects.update_or_create(
        user=user,
        defaults={
            'ip_address': ip_address,
            'latitude': lat,
            'longitude': lng
        }
    )
    return Response({
        'message': 'Location saved' if created else 'Location updated',
        'latitude': lat,
        'longitude': lng,
    })



@api_view(['GET'])
def get_all_locations(request):
    rider = UserLocation.objects.filter(user__role='customer').first()
    driver = UserLocation.objects.filter(user__role='driver').first()

    return Response({
        "rider": {
            "lat": rider.latitude,
            "lng": rider.longitude,
        },
        "driver": {
            "lat": driver.latitude,
            "lng": driver.longitude,
        }
    })
