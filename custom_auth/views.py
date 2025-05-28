from datetime import timedelta, timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from .serializers import RegisterSerializer,LoginSerializer,LogoutSerializer
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from custom_auth.models import OTP, User,PasswordResetOTP
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from custom_auth.utils import send_otp_email
from django.utils import timezone

#signup apis
@permission_classes([AllowAny]) #ignore global permission ,if is add this its ignore golbal permission which is only otp verified user can use this api
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAdminUser])
class UserRoleFilterView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Optional if you use ,you have to login 

    def get(self, request):
        role = request.GET.get('role')
        if not role:
            return Response({'error': 'Role parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(role=role)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


#for login api
@permission_classes([AllowAny])
class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#otp verify

@permission_classes([AllowAny])
class VerifyOTPView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        otp_code = request.data.get("otp")

        if not user_id or not otp_code:
            return Response({"message": "user_id and OTP are required."}, status=400)

        try:
            user = User.objects.get(id=user_id)
            otp_obj = OTP.objects.get(user=user)
        except (User.DoesNotExist, OTP.DoesNotExist):
            return Response({"message": "Invalid user or OTP."}, status=404)

        if otp_obj.code != otp_code:
            return Response({"message": "Incorrect OTP."}, status=400)

        if otp_obj.is_expired():
            return Response({"message": "OTP has expired."}, status=400)

        otp_obj.is_verified = True
        otp_obj.save()

        # ✅ Now issue tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "OTP verified successfully.",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "phone": user.phone,
                "role": user.role
            }
        }, status=200)

#logout
@permission_classes([AllowAny])
class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data['refresh']
                token = RefreshToken(refresh_token)
                token.blacklist()  # Important step
                return Response({"detail": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
            except TokenError:
                return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class ResetPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({'error': 'Both old and new passwords are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)


#forgot password send otp and check valid or not and then send otp

@permission_classes([AllowAny]) 
class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        otp = get_random_string(length=6, allowed_chars='1234567890')

        otp_entry, created = PasswordResetOTP.objects.update_or_create(
            user=user,
            is_verified=False,
            defaults={'otp': otp}
        )

        # # Send OTP via email
        send_otp_email(email, otp)

        
        return Response({'message': 'OTP sent to your email address.'}, status=status.HTTP_200_OK)

#reset password if otp match then new password change
class ResetPasswordWithOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            otp_entry = PasswordResetOTP.objects.filter(user=user, otp=otp, is_verified=False).latest('created_at')
        except PasswordResetOTP.DoesNotExist:
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        #Optional: check OTP expiration (e.g., 10 minutes)
        if timezone.now() - otp_entry.created_at > timedelta(minutes=10):
            return Response({'error': 'OTP expired'}, status=400)

        user.set_password(new_password)
        user.save()
        otp_entry.is_verified = True
        otp_entry.save()

        return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)
