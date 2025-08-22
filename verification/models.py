from django.db import models
from django.contrib.auth import get_user_model
import uuid


# Get the user model regardless of custom user model
User = get_user_model()


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verification_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Email token for {self.user.email} ({'used' if self.is_used else 'unused'})"


class VerificationRequest(models.Model):
    """User requests for identity verification"""
    VERIFICATION_TYPES = [
        ('identity', 'Identity Verification'),
        ('human', 'Human Verification'),
        ('phone', 'Phone Verification'),
        ('email', 'Email Verification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_requests')
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='processed_verifications'
    )
    notes = models.TextField(blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'verification_verification_request'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.verification_type} ({self.status})"


class IdentityDocument(models.Model):
    """Identity documents submitted for verification"""
    DOCUMENT_TYPES = [
        ('passport', 'Passport'),
        ('drivers_license', 'Driver\'s License'),
        ('national_id', 'National ID'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verification_request = models.ForeignKey(
        VerificationRequest, on_delete=models.CASCADE, related_name='documents'
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=100, blank=True)
    issuing_country = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    document_image = models.ImageField(upload_to='verification/documents/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'verification_identity_document'
    
    def __str__(self):
        return f"{self.document_type} for {self.verification_request.user.email}"


class HumanVerification(models.Model):
    """Human verification challenges (CAPTCHA, etc.)"""
    CHALLENGE_TYPES = [
        ('captcha', 'CAPTCHA'),
        ('puzzle', 'Puzzle'),
        ('question', 'Question'),
        ('image', 'Image Recognition'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verification_request = models.ForeignKey(
        VerificationRequest, on_delete=models.CASCADE, related_name='human_verifications'
    )
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    challenge_data = models.JSONField()  # Challenge-specific data
    user_response = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'verification_human_verification'
    
    def __str__(self):
        return f"{self.challenge_type} for {self.verification_request.user.email}"


class VerificationSession(models.Model):
    """Active verification sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_sessions')
    session_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'verification_verification_session'
        indexes = [
            models.Index(fields=['session_token']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Session for {self.user.email} ({'active' if self.is_active else 'expired'})"
