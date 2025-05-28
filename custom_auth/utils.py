from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from decouple import config
import urllib3
urllib3.disable_warnings()

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
# ------------------------- not for development use--------
import ssl
import certifi
import os

os.environ['SSL_CERT_FILE'] = certifi.where()
#----------------------------------- worning---------------------------
def send_otp_email(to_email, otp_code):
    message = Mail(
        from_email=config('DEFAULT_FROM_EMAIL'),
        to_emails=to_email,
        subject='Your OTP Code for TukuGO',
        html_content=f'<p>Your OTP is <strong>{otp_code}</strong>. It is valid for 10 minutes.</p>'
    )

    try:
        sg = SendGridAPIClient(config('SENDGRID_API_KEY_New'))
        response = sg.send(message)
        print(f"[SendGrid] Sent OTP to {to_email}: Status {response.status_code}")
        return True
    except Exception as e:
        print(f"[SendGrid Error] Failed to send OTP: {str(e)}")
        return False
