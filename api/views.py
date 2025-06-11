from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError
from .models import Climate, Planet, Terrain
from .serializers import ClimateSerializer, PlanetSerializer, TerrainSerializer
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
import logging

logger = logging.getLogger(__name__)

# Create your views here.
@api_view(['GET'])
def health_check(request):
    """
    A simple health check endpoint to verify that the API is running.
    """
    return Response({"status": "ok"}, status=200)

class BaseViewSetMixin:
    """Base mixin with common error handling for all ViewSets"""
    
    def handle_validation_error(self, e, action_name="operation"):
        """Handle validation errors with descriptive messages"""
        if hasattr(e, 'detail'):
            if isinstance(e.detail, dict):
                # Field-specific errors
                error_details = {}
                for field, errors in e.detail.items():
                    if isinstance(errors, list):
                        error_details[field] = errors
                    else:
                        error_details[field] = [str(errors)]
                
                return Response({
                    'error': f'Validation failed for {action_name}',
                    'message': 'Please correct the following errors:',
                    'details': error_details
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # General validation error
                return Response({
                    'error': f'Validation failed for {action_name}',
                    'message': str(e.detail),
                    'details': {}
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': f'Validation failed for {action_name}',
                'message': str(e),
                'details': {}
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def handle_integrity_error(self, e, action_name="operation"):
        """Handle database integrity errors"""
        error_message = str(e).lower()
        
        if 'unique' in error_message or 'duplicate' in error_message:
            if 'name' in error_message:
                return Response({
                    'error': 'Duplicate name',
                    'message': f'An item with this name already exists. Names must be unique.',
                    'code': 'DUPLICATE_NAME'
                }, status=status.HTTP_409_CONFLICT)
            else:
                return Response({
                    'error': 'Duplicate entry',
                    'message': f'This {action_name} would create a duplicate entry.',
                    'code': 'DUPLICATE_ENTRY'
                }, status=status.HTTP_409_CONFLICT)
        else:
            logger.error(f"Integrity error in {action_name}: {str(e)}")
            return Response({
                'error': 'Database constraint violation',
                'message': f'The {action_name} violates database constraints.',
                'code': 'CONSTRAINT_VIOLATION'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def handle_not_found_error(self, model_name="resource"):
        """Handle 404 errors with descriptive messages"""
        return Response({
            'error': 'Not found',
            'message': f'The requested {model_name} does not exist.',
            'code': 'NOT_FOUND'
        }, status=status.HTTP_404_NOT_FOUND)
    
    def handle_generic_error(self, e, action_name="operation"):
        """Handle unexpected errors"""
        logger.error(f"Unexpected error in {action_name}: {str(e)}")
        return Response({
            'error': 'Internal server error',
            'message': f'An unexpected error occurred during {action_name}.',
            'code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PlanetViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for Planet CRUD operations
    Provides: list, create, retrieve, update, partial_update, destroy
    """
    queryset = Planet.objects.all()
    serializer_class = PlanetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'population']
    ordering_fields = ['id', 'name', 'created_at', 'updated_at']
    ordering = ['id']
    
    def create(self, request, *args, **kwargs):
        """Create a new planet with proper error handling"""
        try:
            if not request.data or 'name' not in request.data:
                return Response({
                    'error': 'Missing required field',
                    'message': 'Terrain name is required.',
                    'details': {'name': ['This field is required.']},
                    'code': 'MISSING_REQUIRED_FIELD'
                }, status=status.HTTP_400_BAD_REQUEST)
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return self.handle_validation_error(e, "terrain creation")
        except IntegrityError as e:
            return self.handle_integrity_error(e, "terrain creation")
        except Exception as e:
            return self.handle_generic_error(e, "terrain creation")
    
    def update(self, request, *args, **kwargs):
        """Update planet with proper error handling"""
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return self.handle_validation_error(e, "terrain update")
        except IntegrityError as e:
            return self.handle_integrity_error(e, "terrain update")
        except Exception as e:
            return self.handle_generic_error(e, "terrain update")
        
class TerrainViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Terrain.objects.all()
    serializer_class = TerrainSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'created_at', 'updated_at']
    ordering = ['id']

    @action(detail=True, methods=['get'])
    def planets(self, request, pk=None):
        """
        Custom action to get all planets with a specific terrain.
        """
        terrain = self.get_object()
        planets = terrain.planet_set.all()
        serializer = PlanetSerializer(planets, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Create a new terrain with proper error handling"""
        try:
            if not request.data or 'name' not in request.data:
                return Response({
                    'error': 'Missing required field',
                    'message': 'Terrain name is required.',
                    'details': {'name': ['This field is required.']},
                    'code': 'MISSING_REQUIRED_FIELD'
                }, status=status.HTTP_400_BAD_REQUEST)
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return self.handle_validation_error(e, "terrain creation")
        except IntegrityError as e:
            return self.handle_integrity_error(e, "terrain creation")
        except Exception as e:
            return self.handle_generic_error(e, "terrain creation")
    
    def update(self, request, *args, **kwargs):
        """Update terrain with proper error handling"""
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return self.handle_validation_error(e, "terrain update")
        except IntegrityError as e:
            return self.handle_integrity_error(e, "terrain update")
        except Exception as e:
            return self.handle_generic_error(e, "terrain update")
    
class ClimateViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Climate.objects.all()
    serializer_class = ClimateSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'created_at', 'updated_at']
    ordering = ['id']

    def create(self, request, *args, **kwargs):
        """Create a new climate with proper error handling"""
        try:
            if not request.data or 'name' not in request.data:
                return Response({
                    'error': 'Missing required field',
                    'message': 'Climate name is required.',
                    'details': {'name': ['This field is required.']},
                    'code': 'MISSING_REQUIRED_FIELD'
                }, status=status.HTTP_400_BAD_REQUEST)
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return self.handle_validation_error(e, "climate creation")
        except IntegrityError as e:
            return self.handle_integrity_error(e, "climate creation")
        except Exception as e:
            return self.handle_generic_error(e, "climate creation")
        
    def update(self, request, *args, **kwargs):
        """Update climate with proper error handling"""
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return self.handle_validation_error(e, "climate update")
        except IntegrityError as e:
            return self.handle_integrity_error(e, "climate update")
        except Exception as e:
            return self.handle_generic_error(e, "climate update")

    @action(detail=True, methods=['get'])
    def planets(self, request, pk=None):
        """
        Custom action to get all planets with a specific climate.
        """
        climate = self.get_object()
        planets = climate.planet_set.all()
        serializer = PlanetSerializer(planets, many=True)
        return Response(serializer.data)
