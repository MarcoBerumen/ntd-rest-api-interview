from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError
from api.models import Climate, Planet, Terrain
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from api.serializers import PlanetSerializer, TerrainSerializer, ClimateSerializer
from django.urls import reverse

class BaseModelTestCase(TestCase):

    def setUp(self):
        self.planet = Planet.objects.create(
            name="Test Planet",
            population="1000000"
        )

    def test_created_at_auto_populated(self):
        """Test that created_at is automatically set"""
        self.assertIsNotNone(self.planet.created_at)
        self.assertLessEqual(self.planet.created_at, timezone.now())
    
    def test_updated_at_auto_populated(self):
        """Test that updated_at is automatically set"""
        self.assertIsNotNone(self.planet.updated_at)
        self.assertLessEqual(self.planet.updated_at, timezone.now())
    
    def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when model is saved"""
        original_updated_at = self.planet.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.001)
        
        self.planet.population = "1000000"
        self.planet.save()
        
        self.assertGreater(self.planet.updated_at, original_updated_at)


class PlanetModelTestCase(TestCase):
    """Test Planet model functionality"""
    
    def setUp(self):
        self.terrain1 = Terrain.objects.create(name="Desert")
        self.terrain2 = Terrain.objects.create(name="Mountains")
        self.climate1 = Climate.objects.create(name="Arid")
        self.climate2 = Climate.objects.create(name="Temperate")
    
    def test_planet_creation(self):
        """Test basic planet creation"""
        planet = Planet.objects.create(
            name="Tatooine",
            population="200000"
        )
        
        self.assertEqual(planet.name, "Tatooine")
        self.assertEqual(planet.population, "200000")
        self.assertIsNotNone(planet.created_at)
        self.assertIsNotNone(planet.updated_at)
    
    def test_planet_str_representation(self):
        """Test planet string representation"""
        planet = Planet.objects.create(name="Tatooine")
        self.assertEqual(str(planet), "Tatooine")
    
    def test_planet_name_unique_constraint(self):
        """Test that planet names must be unique"""
        Planet.objects.create(name="Tatooine")
        
        with self.assertRaises(IntegrityError):
            Planet.objects.create(name="Tatooine")
    
    def test_planet_population_can_be_null(self):
        """Test that population can be null"""
        planet = Planet.objects.create(name="Unknown Planet")
        self.assertIsNone(planet.population)
    
    def test_planet_terrain_relationship(self):
        """Test many-to-many relationship with terrains"""
        planet = Planet.objects.create(name="Tatooine")
        planet.terrains.add(self.terrain1, self.terrain2)
        
        self.assertEqual(planet.terrains.count(), 2)
        self.assertIn(self.terrain1, planet.terrains.all())
        self.assertIn(self.terrain2, planet.terrains.all())
    
    def test_planet_climate_relationship(self):
        """Test many-to-many relationship with climates"""
        planet = Planet.objects.create(name="Hoth")
        planet.climates.add(self.climate1)
        
        self.assertEqual(planet.climates.count(), 1)
        self.assertIn(self.climate1, planet.climates.all())
    
    def test_planet_ordering(self):
        """Test default ordering by name"""
        Planet.objects.create(name="Zebra Planet")
        Planet.objects.create(name="Alpha Planet")
        Planet.objects.create(name="Beta Planet")
        
        planets = Planet.objects.all()
        planet_names = [planet.name for planet in planets]
        
        self.assertEqual(planet_names, ["Alpha Planet", "Beta Planet", "Zebra Planet"])
    
    def test_planet_can_have_multiple_terrains_and_climates(self):
        """Test complex relationships"""
        planet = Planet.objects.create(name="Diverse Planet")
        planet.terrains.set([self.terrain1, self.terrain2])
        planet.climates.set([self.climate1, self.climate2])
        
        self.assertEqual(planet.terrains.count(), 2)
        self.assertEqual(planet.climates.count(), 2)


class TerrainModelTestCase(TestCase):
    """Test Terrain model functionality"""
    
    def test_terrain_creation(self):
        """Test basic terrain creation"""
        terrain = Terrain.objects.create(name="Forest")
        
        self.assertEqual(terrain.name, "Forest")
        self.assertIsNotNone(terrain.created_at)
        self.assertIsNotNone(terrain.updated_at)
    
    def test_terrain_str_representation(self):
        """Test terrain string representation"""
        terrain = Terrain.objects.create(name="Ocean")
        self.assertEqual(str(terrain), "Ocean")
    
    def test_terrain_name_unique_constraint(self):
        """Test that terrain names must be unique"""
        Terrain.objects.create(name="Desert")
        
        with self.assertRaises(IntegrityError):
            Terrain.objects.create(name="Desert")
    
    def test_terrain_ordering(self):
        """Test default ordering by name"""
        Terrain.objects.create(name="Swamp")
        Terrain.objects.create(name="Desert")
        Terrain.objects.create(name="Forest")
        
        terrains = Terrain.objects.all()
        terrain_names = [terrain.name for terrain in terrains]
        
        self.assertEqual(terrain_names, ["Desert", "Forest", "Swamp"])


class ClimateModelTestCase(TestCase):

    """Test Climate model functionality"""
    
    def test_climate_creation(self):
        """Test basic climate creation"""
        climate = Climate.objects.create(name="Tropical")
        
        self.assertEqual(climate.name, "Tropical")
        self.assertIsNotNone(climate.created_at)
        self.assertIsNotNone(climate.updated_at)
    
    def test_climate_str_representation(self):
        """Test climate string representation"""
        climate = Climate.objects.create(name="Arctic")
        self.assertEqual(str(climate), "Arctic")
    
    def test_climate_name_unique_constraint(self):
        """Test that climate names must be unique"""
        Climate.objects.create(name="Temperate")
        
        with self.assertRaises(IntegrityError):
            Climate.objects.create(name="Temperate")
    
    def test_climate_ordering(self):
        """Test default ordering by name"""
        Climate.objects.create(name="Tropical")
        Climate.objects.create(name="Arctic")
        Climate.objects.create(name="Temperate")
        
        climates = Climate.objects.all()
        climate_names = [climate.name for climate in climates]
        
        self.assertEqual(climate_names, ["Arctic", "Temperate", "Tropical"])



    """Test custom serializer validation"""
    
    def test_planet_name_normalization(self):
        """Test that planet names are properly normalized"""
        test_cases = [
            ('  Normal Name  ', 'Normal Name'),
            ('\tTabbed\t', 'Tabbed'),
            ('Multiple   Spaces', 'Multiple   Spaces'),  # Internal spaces preserved
        ]
        
        for input_name, expected_name in test_cases:
            data = {'name': input_name, 'population': '1000'}
            serializer = PlanetSerializer(data=data)
            
            self.assertTrue(serializer.is_valid(), 
                          f"Failed for input: '{input_name}'. Errors: {serializer.errors}")
            
            planet = serializer.save()
            self.assertEqual(planet.name, expected_name)
            
            # Clean up for next iteration
            planet.delete()
    
    def test_serializer_context_usage(self):
        """Test using serializer context for custom behavior"""
        terrain = Terrain.objects.create(name="Test Terrain")
        
        # Test with context
        context = {'request': type('MockRequest', (), {'user': None})()}
        data = {
            'name': 'Context Test Planet',
            'terrain_ids': [terrain.id]
        }
        
        serializer = PlanetSerializer(data=data, context=context)
        self.assertTrue(serializer.is_valid())
        
        planet = serializer.save()
        self.assertEqual(planet.name, 'Context Test Planet')

    """Test Climate API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.climate1 = Climate.objects.create(name="Arid")
        self.climate2 = Climate.objects.create(name="Temperate")
    
    def test_get_climate_list(self):
        """Test retrieving list of climates"""
        url = reverse('climate-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_create_climate(self):
        """Test creating a new climate"""
        url = reverse('climate-list')
        data = {'name': 'Tropical'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Climate.objects.count(), 3)
        self.assertTrue(Climate.objects.filter(name='Tropical').exists())