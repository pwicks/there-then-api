from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class User(AbstractUser):
    """Custom user model with verification status"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Override username field to use email as primary identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    class Meta:
        db_table = 'core_user'


class GeographicArea(models.Model):
    """Geographic areas where users can leave/find messages"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True)
    geometry = models.PolygonField(spatial_index=True)
    start_year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    end_year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    start_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        null=True, blank=True
    )
    end_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        null=True, blank=True
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_areas'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_geographic_area'
        indexes = [
            models.Index(fields=['start_year', 'end_year']),
            models.Index(fields=['start_month', 'end_month']),
        ]
    
    def __str__(self):
        return f"{self.name or 'Unnamed Area'} ({self.start_year}-{self.end_year})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_year > self.end_year:
            raise ValidationError("Start year must be before or equal to end year")
        if self.start_month and self.end_month:
            if self.start_year == self.end_year and self.start_month > self.end_month:
                raise ValidationError("Start month must be before or equal to end month in same year")


class UserLocation(models.Model):
    """Records of where users have been"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    area = models.ForeignKey(GeographicArea, on_delete=models.CASCADE, related_name='visitors')
    visited_year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    visited_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'core_user_location'
        unique_together = ['user', 'area', 'visited_year', 'visited_month']
        indexes = [
            models.Index(fields=['visited_year', 'visited_month']),
        ]
    
    def __str__(self):
        return f"{self.user.email} at {self.area} in {self.visited_year}"
