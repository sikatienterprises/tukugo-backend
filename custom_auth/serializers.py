from rest_framework import serializers

from custom_auth.utils import send_otp_email
from .models import User

from django.contrib.auth import authenticate,get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

#signup api 
class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone','username', 'password', 'confirm_password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    #save user
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user


#user info api through roles
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone', 'role']


#for login api

User = get_user_model()
import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from custom_auth.models import OTP  # Make sure this is correct

User = get_user_model()

def generate_otp():
    return str(random.randint(100000, 999999))

class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username_or_email = data.get('username_or_email')
        password = data.get('password')

        # Try to get user by email, fallback to username
        try:
            user = User.objects.get(email=username_or_email)
            username = user.username
        except User.DoesNotExist:
            username = username_or_email

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User is inactive")

        # ✅ Generate and store OTP
        otp_code = generate_otp()
        expires_at = timezone.now() + timedelta(minutes=5)

        OTP.objects.update_or_create(
            user=user,
            defaults={
                'code': otp_code,
                'expires_at': expires_at,
                'is_verified': False
            }
        )
        send_otp_email(user.email, otp_code)


        # ✅ Simulate sending OTP to email
        print(f"Sending OTP {otp_code} to Email address: {user.email}")  # Replace with actual SMS logic

        # ✅ Return message + user_id only
        return {
            "message": "OTP sent to your email address.",
            "user_id": user.id
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()