import random
from django.utils import timezone
from datetime import timedelta

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_to_phone(phone, otp_code):
    # Replace this with actual SMS logic using Twilio, MSG91, etc.
    print(f"Sending OTP {otp_code} to {phone}")

def get_otp_expiry():
    return timezone.now() + timedelta(minutes=5)
