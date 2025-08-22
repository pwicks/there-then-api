from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from .models import EmailVerificationToken, User
import datetime

def request_email_verification(user):
	token = get_random_string(48)
	expires_at = timezone.now() + datetime.timedelta(hours=24)
	EmailVerificationToken.objects.create(user=user, token=token, expires_at=expires_at)
	verification_url = f"{settings.SITE_URL}/verify-email/{token}/"
	send_mail(
		subject="Verify your email",
		message=f"Please verify your email by clicking the following link: {verification_url}",
		from_email=settings.DEFAULT_FROM_EMAIL,
		recipient_list=[user.email],
		fail_silently=False,
	)
	return token

def verify_email(request, token):
    email_token = get_object_or_404(EmailVerificationToken, token=token, is_used=False)
    if email_token.expires_at < timezone.now():
        return HttpResponse("Verification link expired.", status=400)
    email_token.is_used = True
    email_token.save()
    # Mark user as verified
    user = email_token.user
    user.is_verified = True
    user.save()
    return HttpResponse("Email verified successfully.")
