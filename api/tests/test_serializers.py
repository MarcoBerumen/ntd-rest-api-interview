from django.test import TestCase
from rest_framework.exceptions import ValidationError
from ..models import Planet, Climate, Terrain
from ..serializers import PlanetSerializer, ClimateSerializer, TerrainSerializer


class ClimateSerializerTest(TestCase):
    """Test ClimateSerializer functionality"""
    
    def test_climate_serialization(self):
        """Test serializing a climate object"""
        climate = Climate.objects.create(name="Tropical")
        serializer = ClimateSerializer(climate)
        
        self.assertEqual(serializer.data['name'], "Tropical")
        self.assertIn('created_at', serializer.data)
        self.assertIn('updated_at', serializer.data)
    
    def test_climate_deserialization(self):
        """Test deserializing climate data"""
        data = {'name': 'Arctic'}
        serializer = ClimateSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        climate = serializer.save()
        self.assertEqual(climate.name, "Arctic")


class TerrainSerializerTest(TestCase):
    """Test TerrainSerializer functionality"""
    
    def test_terrain_serialization(self):
        """Test serializing a terrain object"""
        terrain = Terrain.objects.create(name="Forest")
        serializer = TerrainSerializer(terrain)
        
        self.assertEqual(serializer.data['name'], "Forest")
        self.assertIn('created_at', serializer.data)
        self.assertIn('updated_at', serializer.data)
    
    def test_terrain_deserialization(self):
        """Test deserializing terrain data"""
        data = {'name': 'Swamp'}
        serializer = TerrainSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        terrain = serializer.save()
        self.assertEqual(terrain.name, "Swamp")


class PlanetSerializerTest(TestCase):
    """Test PlanetSerializer functionality"""
    
    def setUp(self):
        self.climate1 = Climate.objects.create(name="Arid")
        self.climate2 = Climate.objects.create(name="Temperate")
        self.terrain1 = Terrain.objects.create(name="Desert")
        self.terrain2 = Terrain.objects.create(name="Mountains")
    
    def test_planet_serialization_basic(self):
        """Test serializing a basic planet object"""
        planet = Planet.objects.create(name="Tatooine", population="200000")
        serializer = PlanetSerializer(planet)
        
        self.assertEqual(serializer.data['name'], "Tatooine")
        self.assertEqual(serializer.data['population'], "200000")
        self.assertEqual(serializer.data['climates'], [])
        self.assertEqual(serializer.data['terrains'], [])
    
    def test_planet_serialization_with_relationships(self):
        """Test serializing a planet with climates and terrains"""
        planet = Planet.objects.create(name="Earth", population="7800000000")
        planet.climates.add(self.climate1, self.climate2)
        planet.terrains.add(self.terrain1, self.terrain2)
        
        serializer = PlanetSerializer(planet)
        
        self.assertEqual(len(serializer.data['climates']), 2)
        self.assertIn("Arid", serializer.data['climates'])
        self.assertIn("Temperate", serializer.data['climates'])
        self.assertEqual(len(serializer.data['terrains']), 2)
        self.assertIn("Desert", serializer.data['terrains'])
        self.assertIn("Mountains", serializer.data['terrains'])
    
    def test_planet_deserialization_basic(self):
        """Test deserializing basic planet data"""
        data = {
            'name': 'Mars',
            'population': '0'
        }
        serializer = PlanetSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        planet = serializer.save()
        self.assertEqual(planet.name, "Mars")
        self.assertEqual(planet.population, "0")
    
    def test_planet_deserialization_with_existing_relationships(self):
        """Test deserializing planet data with existing climates and terrains"""
        data = {
            'name': 'Venus',
            'population': '0',
            'climates': ['Arid'],
            'terrains': ['Desert']
        }
        serializer = PlanetSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        planet = serializer.save()
        
        self.assertEqual(planet.climates.count(), 1)
        self.assertEqual(planet.climates.first().name, "Arid")
        self.assertEqual(planet.terrains.count(), 1)
        self.assertEqual(planet.terrains.first().name, "Desert")
    
    def test_planet_deserialization_creates_new_relationships(self):
        """Test that serializer creates new climates and terrains if they don't exist"""
        data = {
            'name': 'Jupiter',
            'population': '0',
            'climates': ['Gas Giant'],
            'terrains': ['Gas']
        }
        serializer = PlanetSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        planet = serializer.save()
        
        # Check that new climate and terrain were created
        self.assertTrue(Climate.objects.filter(name="Gas Giant").exists())
        self.assertTrue(Terrain.objects.filter(name="Gas").exists())
        
        self.assertEqual(planet.climates.first().name, "Gas Giant")
        self.assertEqual(planet.terrains.first().name, "Gas")
    
    def test_planet_update_serializer(self):
        """Test updating a planet through the serializer"""
        planet = Planet.objects.create(name="Original", population="1000")
        planet.climates.add(self.climate1)
        
        data = {
            'name': 'Updated Planet',
            'population': '2000',
            'climates': ['Temperate'],
            'terrains': ['Mountains']
        }
        
        serializer = PlanetSerializer(instance=planet, data=data)
        self.assertTrue(serializer.is_valid())
        updated_planet = serializer.save()
        
        self.assertEqual(updated_planet.name, "Updated Planet")
        self.assertEqual(updated_planet.population, "2000")
        self.assertEqual(updated_planet.climates.count(), 1)
        self.assertEqual(updated_planet.climates.first().name, "Temperate")
        self.assertEqual(updated_planet.terrains.count(), 1)
        self.assertEqual(updated_planet.terrains.first().name, "Mountains")