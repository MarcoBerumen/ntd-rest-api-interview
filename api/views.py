from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError
from .models import Planet
from .serializers import PlanetSerializer

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
    # filterset_fields = ['terrains', 'climates']
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
    
    # @action(detail=False, methods=['get'])
    # def by_terrain(self, request):
    #     """Custom endpoint to get planets by specific terrain"""
    #     terrain = request.query_params.get('terrain')
    #     if not terrain:
    #         return Response(
    #             {'error': 'terrain parameter is required'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
        
    #     planets = Planet.objects.filter(terrains__contains=[terrain])
    #     serializer = self.get_serializer(planets, many=True)
    #     return Response(serializer.data)
    
    # @action(detail=False, methods=['get'])
    # def by_climate(self, request):
    #     """Custom endpoint to get planets by specific climate"""
    #     climate = request.query_params.get('climate')
    #     if not climate:
    #         return Response(
    #             {'error': 'climate parameter is required'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
        
    #     planets = Planet.objects.filter(climates__contains=[climate])
    #     serializer = self.get_serializer(planets, many=True)
    #     return Response(serializer.data)