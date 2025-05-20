from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Notification
from .serializers import NotificationSerializer
from  .models import models
from django.db.models import Q
from rest_framework.permissions import IsAdminUser

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    user = request.user

    # If user is a driver
    if user.role =='driver':
        driver = user.driver_profile
        print("print",driver)

        notifications = Notification.objects.filter(
            models.Q(send_to_all=True) |
            models.Q(send_to_drivers=True) |
            models.Q(vehicle_type=driver.vehicle_type) |
            models.Q(target_driver=driver)
        ).order_by('-created_at')
    else:
        # For customers
        notifications = Notification.objects.filter(
            models.Q(send_to_all=True) |
            models.Q(send_to_customers=True) |
            models.Q(target_user=user)
        ).order_by('-created_at')

    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAdminUser])
def send_notification(request):
    title = request.data.get('title')
    message = request.data.get('message')
    send_to_all = request.data.get('send_to_all', False)
    send_to_customers = request.data.get('send_to_customers', False)
    send_to_drivers = request.data.get('send_to_drivers', False)
    target_user_id = request.data.get('target_user_id')  # Optional
    target_driver_id = request.data.get('target_driver_id')  # Optional
    vehicle_type = request.data.get('vehicle_type')  # Optional (bike, car etc.)

    if not title or not message:
        return Response({"error": "Title and Message are required"}, status=status.HTTP_400_BAD_REQUEST)

    notification = Notification.objects.create(
        title=title,
        message=message,
        send_to_all=send_to_all,
        send_to_customers=send_to_customers,
        send_to_drivers=send_to_drivers,
        vehicle_type=vehicle_type
    )

    # If sending to a particular customer
    if target_user_id:
        from custom_auth.models import User  #
        try:
            user = User.objects.get(id=target_user_id)
            notification.target_user = user
            notification.save()
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

    # If sending to a particular driver
    if target_driver_id:
        from driver.models import Driver  # Import your Driver model
        try:
            driver = Driver.objects.get(id=target_driver_id)
            notification.target_driver = driver
            notification.save()
        except Driver.DoesNotExist:
            return Response({"error": "Driver not found"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Notification sent successfully"}, status=status.HTTP_201_CREATED)
