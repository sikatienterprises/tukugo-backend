from django.urls import path
from .views import RegisterView,UserRoleFilterView,LoginAPIView,VerifyOTPView,LogoutAPIView

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


]
