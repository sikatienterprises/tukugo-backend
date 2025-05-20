from rest_framework import serializers
from .models import Customer,Ride
from custom_auth.models import User
from driver.models import Driver

class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user', 'address', 'city', 'created_at']
        read_only_fields = ['id','user','created_at']



#for ride booking
class RideRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = [
            'id', 'pickup_location', 'drop_location', 'pickup_lat', 'pickup_lng',
            'drop_lat', 'drop_lng', 'vehicle_type'
        ]



class DriverSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username')  # or user.username/email

    class Meta:
        model = Driver
        fields = ['name', 'license_number', 'vehicle_number', 'vehicle_type', 'city']

class CaptainDetailsSerializer(serializers.ModelSerializer):
    driver = DriverSerializer()

    class Meta:
        model = Ride
        fields = ['id', 'driver']


from custom_auth.serializers import UserSerializer  # Optional: if you want to show customer/driver details

class RideSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    driver_name = serializers.CharField(source='driver.user.username', read_only=True)
    
    class Meta:
        model = Ride
        fields = [
            'id',
            'pickup_location',
            'drop_location',
            'vehicle_type',
            'fare',
            'status',
            'customer_name',
            'driver_name',
        ]