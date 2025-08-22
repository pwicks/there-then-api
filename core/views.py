from typing import Any

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from .models import User, GeographicArea, UserLocation
from .serializers import (
    UserSerializer, UserCreateSerializer, GeographicAreaSerializer,
    GeographicAreaCreateSerializer, UserLocationSerializer, UserLocationCreateSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self) -> type:
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self) -> list[permissions.BasePermission]:
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def me(self, request: dict[str, Any]) -> Response:
        """Get current user information"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request: dict[str, Any]) -> Response:
        """Update current user profile"""
        serializer: UserSerializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GeographicAreaViewSet(viewsets.ModelViewSet):
    """ViewSet for GeographicArea model"""
    queryset = GeographicArea.objects.all()
    serializer_class = GeographicAreaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GeographicAreaCreateSerializer
        return GeographicAreaSerializer
    
    @action(detail=False, methods=['post'])
    def search_by_location(self, request: dict[str, Any]) -> Response:
        """Search for areas by geographic location"""
        try:
            # Get coordinates from request
            lat = float(request.data.get('latitude'))
            lng = float(request.data.get('longitude'))
            radius_km = float(request.data.get('radius_km', 10))
            
            # Create a point from coordinates
            from django.contrib.gis.geos import Point
            point = Point(lng, lat, srid=4326)
            
            # Find areas within radius
            areas = GeographicArea.objects.filter(
                geometry__distance_lte=(point, D(km=radius_km))
            ).annotate(
                distance=Distance('geometry', point)
            ).order_by('distance')
            
            serializer = self.get_serializer(areas, many=True)
            return Response(serializer.data)
            
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid coordinates or radius'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def search_by_time(self, request: dict[str, Any]) -> Response:
        """Search for areas by time period"""
        try:
            start_year = request.data.get('start_year')
            end_year = request.data.get('end_year')
            start_month = request.data.get('start_month')
            end_month = request.data.get('end_month')
            
            queryset = GeographicArea.objects.all()
            
            if start_year:
                queryset = queryset.filter(start_year__lte=start_year)
            if end_year:
                queryset = queryset.filter(end_year__gte=end_year)
            if start_month:
                queryset = queryset.filter(start_month__lte=start_month)
            if end_month:
                queryset = queryset.filter(end_month__gte=end_month)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def search_by_intersection(self, request: dict[str, Any]) -> Response:
        """Search for areas that intersect with a given polygon"""
        try:
            geometry_wkt = request.data.get('geometry')
            if not geometry_wkt:
                return Response(
                    {'error': 'Geometry is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            geometry = GEOSGeometry(geometry_wkt)
            areas = GeographicArea.objects.filter(geometry__intersects=geometry)
            
            serializer = self.get_serializer(areas, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Invalid geometry: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserLocationViewSet(viewsets.ModelViewSet):
    """ViewSet for UserLocation model"""
    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserLocationCreateSerializer
        return UserLocationSerializer
    
    def get_queryset(self):
        """Filter queryset to show only current user's locations"""
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_area(self, request: dict[str, Any]) -> Response:
        """Get user locations for a specific area"""
        area_id = request.query_params.get('area_id')
        if not area_id:
            return Response(
                {'error': 'area_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            locations = self.get_queryset().filter(area_id=area_id)
            serializer = self.get_serializer(locations, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
