from django.test import TestCase
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from ..models import Planet, Climate, Terrain


class BaseModelTest(TestCase):
    """Test BaseModel abstract class functionality"""
    
    def test_base_model_timestamps(self):
        """Test that created_at and updated_at are set automatically"""
        planet = Planet.objects.create(name="Test Planet")
        
        self.assertIsNotNone(planet.created_at)
        self.assertIsNotNone(planet.updated_at)
        
        # Update the planet and check that updated_at changes
        original_updated_at = planet.updated_at
        planet.population = "1000"
        planet.save()
        
        self.assertGreater(planet.updated_at, original_updated_at)


class PlanetModelTest(TestCase):
    """Test Planet model functionality"""
    
    def setUp(self):
        self.climate1 = Climate.objects.create(name="Arid")
        self.climate2 = Climate.objects.create(name="Temperate")
        self.terrain1 = Terrain.objects.create(name="Desert")
        self.terrain2 = Terrain.objects.create(name="Mountains")
    
    def test_planet_creation(self):
        """Test basic planet creation"""
        planet = Planet.objects.create(
            name="Tatooine",
            population="200000"
        )
        
        self.assertEqual(planet.name, "Tatooine")
        self.assertEqual(planet.population, "200000")
        self.assertEqual(str(planet), "Tatooine")
    
    def test_planet_name_unique_constraint(self):
        """Test that planet names must be unique"""
        Planet.objects.create(name="Tatooine")
        
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Planet.objects.create(name="Tatooine")
    
    def test_planet_climate_relationships(self):
        """Test many-to-many relationship with climates"""
        planet = Planet.objects.create(name="Earth")
        
        # Add climates
        planet.climates.add(self.climate1, self.climate2)
        
        self.assertEqual(planet.climates.count(), 2)
        self.assertIn(self.climate1, planet.climates.all())
        self.assertIn(self.climate2, planet.climates.all())
    
    def test_planet_terrain_relationships(self):
        """Test many-to-many relationship with terrains"""
        planet = Planet.objects.create(name="Mars")
        
        # Add terrains
        planet.terrains.add(self.terrain1, self.terrain2)
        
        self.assertEqual(planet.terrains.count(), 2)
        self.assertIn(self.terrain1, planet.terrains.all())
        self.assertIn(self.terrain2, planet.terrains.all())
    
    def test_planet_optional_fields(self):
        """Test that population, terrains, and climates are optional"""
        planet = Planet.objects.create(name="Unknown Planet")
        
        self.assertIsNone(planet.population)
        self.assertEqual(planet.climates.count(), 0)
        self.assertEqual(planet.terrains.count(), 0)
    
    def test_planet_ordering(self):
        """Test that planets are ordered by name"""
        Planet.objects.create(name="Zebra Planet")
        Planet.objects.create(name="Alpha Planet")
        Planet.objects.create(name="Beta Planet")
        
        planets = Planet.objects.all()
        names = [planet.name for planet in planets]
        
        self.assertEqual(names, ["Alpha Planet", "Beta Planet", "Zebra Planet"])


class ClimateModelTest(TestCase):
    """Test Climate model functionality"""
    
    def test_climate_creation(self):
        """Test basic climate creation"""
        climate = Climate.objects.create(name="Tropical")
        
        self.assertEqual(climate.name, "Tropical")
        self.assertEqual(str(climate), "Tropical")
    
    def test_climate_name_unique_constraint(self):
        """Test that climate names must be unique"""
        Climate.objects.create(name="Temperate")
        
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Climate.objects.create(name="Temperate")
    
    def test_climate_ordering(self):
        """Test that climates are ordered by name"""
        Climate.objects.create(name="Tropical")
        Climate.objects.create(name="Arid")
        Climate.objects.create(name="Polar")
        
        climates = Climate.objects.all()
        names = [climate.name for climate in climates]
        
        self.assertEqual(names, ["Arid", "Polar", "Tropical"])
    
    def test_climate_planet_relationship(self):
        """Test reverse relationship from climate to planets"""
        climate = Climate.objects.create(name="Temperate")
        planet1 = Planet.objects.create(name="Earth")
        planet2 = Planet.objects.create(name="Mars")
        
        planet1.climates.add(climate)
        planet2.climates.add(climate)
        
        self.assertEqual(climate.planet_set.count(), 2)
        self.assertIn(planet1, climate.planet_set.all())
        self.assertIn(planet2, climate.planet_set.all())


class TerrainModelTest(TestCase):
    """Test Terrain model functionality"""
    
    def test_terrain_creation(self):
        """Test basic terrain creation"""
        terrain = Terrain.objects.create(name="Ocean")
        
        self.assertEqual(terrain.name, "Ocean")
        self.assertEqual(str(terrain), "Ocean")
    
    def test_terrain_name_unique_constraint(self):
        """Test that terrain names must be unique"""
        Terrain.objects.create(name="Desert")
        
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Terrain.objects.create(name="Desert")
    
    def test_terrain_ordering(self):
        """Test that terrains are ordered by name"""
        Terrain.objects.create(name="Ocean")
        Terrain.objects.create(name="Desert")
        Terrain.objects.create(name="Forest")
        
        terrains = Terrain.objects.all()
        names = [terrain.name for terrain in terrains]
        
        self.assertEqual(names, ["Desert", "Forest", "Ocean"])
    
    def test_terrain_planet_relationship(self):
        """Test reverse relationship from terrain to planets"""
        terrain = Terrain.objects.create(name="Mountains")
        planet1 = Planet.objects.create(name="Earth")
        planet2 = Planet.objects.create(name="Mars")
        
        planet1.terrains.add(terrain)
        planet2.terrains.add(terrain)
        
        self.assertEqual(terrain.planet_set.count(), 2)
        self.assertIn(planet1, terrain.planet_set.all())
        self.assertIn(planet2, terrain.planet_set.all())