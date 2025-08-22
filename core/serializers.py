from datetime import datetime
from typing import Any
import pytz

from rest_framework import serializers
from .models import User, GeographicArea, UserLocation


# Please add type hints to the serializers for better clarity

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    This serializer includes fields for user information and verification status.
    It does not include the 'password' field as it is not needed for serialization.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 
                 'is_verified', 'verification_date', 'created_at']
        read_only_fields = ['id', 'is_verified', 'verification_date', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users
    This serializer includes password confirmation and validation.
    It does not include the 'id' field as it is auto-generated.
    It also does not include 'is_verified' or 'verification_date' fields as they are
    set by the system after verification.
    """
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data: dict[str, Any]) -> User:
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class GeographicAreaSerializer(serializers.ModelSerializer):
    """
    Serializer for GeographicArea model
    This serializer includes a read-only field for the geometry in WKT format.
    """
    created_by = UserSerializer(read_only=True)
    geometry_wkt = serializers.SerializerMethodField()
    
    class Meta:
        model = GeographicArea
        fields = ['id', 'name', 'geometry_wkt', 'start_year', 'end_year', 
                 'start_month', 'end_month', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']
    
    def get_geometry_wkt(self, obj: GeographicArea) -> Any:
        return obj.geometry.wkt if obj.geometry else None


class GeographicAreaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new geographic areas
    This serializer accepts geometry in WKT format and converts it to a GEOSGeometry object.
    """
    geometry_wkt = serializers.CharField(write_only=True)
    
    class Meta:
        model = GeographicArea
        fields = ['id', 'name', 'geometry_wkt', 'start_year', 'end_year', 'start_month', 'end_month']
        read_only_fields = ['id']
    
    def create(self, validated_data: dict[str, Any]) -> GeographicArea:
        from django.contrib.gis.geos import GEOSGeometry
        from .models import GeographicArea
        from typing import cast

        if 'created_at' in validated_data and isinstance(validated_data['created_at'], datetime):
            validated_data['created_at'] = validated_data['created_at'].astimezone(pytz.utc)
        elif 'created_at' not in validated_data:
            validated_data['created_at'] = datetime.now(pytz.utc)

        validated_data['created_by'] = self.context['request'].user
        
        geometry_wkt = validated_data.pop('geometry_wkt')
        try:
            geometry = GEOSGeometry(geometry_wkt)
            if not geometry.geom_type == 'Polygon':
                raise serializers.ValidationError("Geometry must be a Polygon")
        except Exception as e:
            raise serializers.ValidationError(f"Invalid geometry: {str(e)}")
        
        validated_data['geometry'] = geometry
        validated_data['created_by'] = self.context['request'].user
        
        return cast(GeographicArea, super().create(validated_data))


class UserLocationSerializer(serializers.ModelSerializer):
    """
    Serializer for UserLocation model
    This serializer includes a read-only field for the user and area.
    It does not accept a user field, as it is inferred from the request context.
    @TODO: Consider whether to display the user or not.
    """
    user = UserSerializer(read_only=True)
    area = GeographicAreaSerializer(read_only=True)
    
    class Meta:
        model = UserLocation
        fields = ['id', 'user', 'area', 'visited_year', 'visited_month', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class UserLocationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new user locations
    User locations have a user and a geographic area.
    This serializer does not accept a user field, as it is inferred from the request context.
    """
    class Meta:
        model = UserLocation
        fields = ['area', 'visited_year', 'visited_month']
    
    def create(self, validated_data: dict[str, Any]) -> UserLocation:
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
