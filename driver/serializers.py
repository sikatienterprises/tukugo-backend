from rest_framework import serializers
from .models import Driver,RiderLocation
from custom_auth.models import User
from customer.models import Ride

#for driver laoction
class DriverSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Driver
        fields = ['id', 'user', 'license_number', 'vehicle_type', 'vehicle_number', 'city', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


#for rider loaction
class RiderLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiderLocation
        fields = ['latitude', 'longitude']

#for ride selection
class RideListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = ['id', 'pickup_location', 'drop_location', 'pickup_lat', 'pickup_lng', 'drop_lat', 'drop_lng', 'vehicle_type','status']


class AcceptRideSerializer(serializers.Serializer):
    ride_id = serializers.IntegerField()
    fare = serializers.DecimalField(max_digits=10, decimal_places=2)
