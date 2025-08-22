from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, GeographicArea, UserLocation


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_verified', 'is_staff', 'created_at']
    list_filter = ['is_verified', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Verification', {'fields': ('is_verified', 'verification_date')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Verification', {'fields': ('is_verified', 'verification_date')}),
    )


@admin.register(GeographicArea)
class GeographicAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_year', 'end_year', 'start_month', 'end_month', 'created_by', 'created_at']
    list_filter = ['start_year', 'end_year', 'start_month', 'end_month', 'created_at']
    search_fields = ['name', 'created_by__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    list_display = ['user', 'area', 'visited_year', 'visited_month', 'created_at']
    list_filter = ['visited_year', 'visited_month', 'created_at']
    search_fields = ['user__email', 'area__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
