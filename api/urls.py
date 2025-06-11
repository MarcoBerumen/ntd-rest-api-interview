from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'planets', views.PlanetViewSet)
router.register(r'terrains', views.TerrainViewSet)
router.register(r'climates', views.ClimateViewSet)

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('', include(router.urls))
]