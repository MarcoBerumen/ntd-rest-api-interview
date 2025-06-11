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

# Create your views here.
@api_view(['GET'])
def health_check(request):
    """
    A simple health check endpoint to verify that the API is running.
    """
    return Response({"status": "ok"}, status=200)



class PlanetViewSet(viewsets.ModelViewSet):
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
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {'error': 'A planet with this name already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """Update planet with proper error handling"""
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {'error': 'A planet with this name already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class TerrainViewSet(viewsets.ModelViewSet):
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
    
class ClimateViewSet(viewsets.ModelViewSet):
    queryset = Climate.objects.all()
    serializer_class = ClimateSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'created_at', 'updated_at']
    ordering = ['id']

    @action(detail=True, methods=['get'])
    def planets(self, request, pk=None):
        """
        Custom action to get all planets with a specific climate.
        """
        climate = self.get_object()
        planets = climate.planet_set.all()
        serializer = PlanetSerializer(planets, many=True)
        return Response(serializer.data)
