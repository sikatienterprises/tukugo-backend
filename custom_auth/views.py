from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from .serializers import RegisterSerializer,LoginSerializer,LogoutSerializer
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from custom_auth.models import OTP, User
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser

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