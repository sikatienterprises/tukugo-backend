from django.urls import path
from .views import RegisterView,UserRoleFilterView,LoginAPIView,VerifyOTPView,LogoutAPIView,ResetPasswordView,ForgotPasswordView,ResetPasswordWithOTPView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('users/', UserRoleFilterView.as_view(), name='user-role-filter'),
    path('login/', LoginAPIView.as_view(), name='login'),
    #for verify otp
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    # create new access token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #logout
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    #reset password
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    #forgot password send email/username
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    #Reset Password with OTP
    path('reset-password-with-otp/', ResetPasswordWithOTPView.as_view(), name='reset-password-with-otp'),





]
