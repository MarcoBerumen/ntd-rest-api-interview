from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from ..models import Planet, Climate, Terrain


class HealthCheckViewTest(TestCase):
    """Test the health check endpoint"""
    
    def test_health_check(self):
        """Test that health check returns OK"""
        response = self.client.get(reverse('health_check'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class PlanetViewSetTest(APITestCase):
    """Test PlanetViewSet CRUD operations"""
    
    def setUp(self):
        self.client = APIClient()
        self.climate1 = Climate.objects.create(name="Arid")
        self.climate2 = Climate.objects.create(name="Temperate")
        self.terrain1 = Terrain.objects.create(name="Desert")
        self.terrain2 = Terrain.objects.create(name="Mountains")
        
        self.planet1 = Planet.objects.create(name="Tatooine", population="200000")
        self.planet1.climates.add(self.climate1)
        self.planet1.terrains.add(self.terrain1)
        
        self.planet2 = Planet.objects.create(name="Earth", population="7800000000")
    
    def test_list_planets(self):
        """Test listing all planets"""
        url = reverse('planet-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_planet(self):
        """Test retrieving a specific planet"""
        url = reverse('planet-detail', kwargs={'pk': self.planet1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Tatooine")
        self.assertEqual(response.data['population'], "200000")
        self.assertIn("Arid", response.data['climates'])
        self.assertIn("Desert", response.data['terrains'])
    
    def test_create_planet_basic(self):
        """Test creating a basic planet"""
        url = reverse('planet-list')
        data = {
            'name': 'Mars',
            'population': '0'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Planet.objects.count(), 3)
        
        planet = Planet.objects.get(name='Mars')
        self.assertEqual(planet.population, '0')
    
    def test_create_planet_with_relationships(self):
        """Test creating a planet with climates and terrains"""
        url = reverse('planet-list')
        data = {
            'name': 'Venus',
            'population': '0',
            'climates': ['Arid', 'Hot'],
            'terrains': ['Desert', 'Volcanic']
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        planet = Planet.objects.get(name='Venus')
        self.assertEqual(planet.climates.count(), 2)
        self.assertEqual(planet.terrains.count(), 2)
        
        # Check that new climate and terrain were created
        self.assertTrue(Climate.objects.filter(name="Hot").exists())
        self.assertTrue(Terrain.objects.filter(name="Volcanic").exists())
    
    def test_create_planet_duplicate_name(self):
        """Test that creating a planet with duplicate name fails"""
        url = reverse('planet-list')
        data = {
            'name': 'Tatooine',  # Already exists
            'population': '300000'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_planet(self):
        """Test updating a planet"""
        url = reverse('planet-detail', kwargs={'pk': self.planet2.pk})
        data = {
            'name': 'Updated Earth',
            'population': '8000000000',
            'climates': ['Temperate'],
            'terrains': ['Mountains', 'Ocean']
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.planet2.refresh_from_db()
        self.assertEqual(self.planet2.name, 'Updated Earth')
        self.assertEqual(self.planet2.population, '8000000000')
        self.assertEqual(self.planet2.climates.count(), 1)
        self.assertEqual(self.planet2.terrains.count(), 2)
    
    def test_partial_update_planet(self):
        """Test partially updating a planet"""
        url = reverse('planet-detail', kwargs={'pk': self.planet1.pk})
        data = {
            'population': '250000'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.planet1.refresh_from_db()
        self.assertEqual(self.planet1.name, 'Tatooine')  # Unchanged
        self.assertEqual(self.planet1.population, '250000')  # Updated
    
    def test_delete_planet(self):
        """Test deleting a planet"""
        url = reverse('planet-detail', kwargs={'pk': self.planet1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Planet.objects.count(), 1)
        self.assertFalse(Planet.objects.filter(pk=self.planet1.pk).exists())
    
    def test_search_planets(self):
        """Test searching planets by name"""
        url = reverse('planet-list')
        response = self.client.get(url, {'search': 'Earth'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Earth')
    
    def test_ordering_planets(self):
        """Test ordering planets"""
        url = reverse('planet-list')
        response = self.client.get(url, {'ordering': '-name'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [planet['name'] for planet in response.data['results']]
        self.assertEqual(names, ['Tatooine', 'Earth'])


class ClimateViewSetTest(APITestCase):
    """Test ClimateViewSet operations"""
    
    def setUp(self):
        self.client = APIClient()
        self.climate = Climate.objects.create(name="Tropical")
        self.planet = Planet.objects.create(name="Tropical Planet")
        self.planet.climates.add(self.climate)
    
    def test_list_climates(self):
        """Test listing all climates"""
        url = reverse('climate-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_climate(self):
        """Test creating a climate"""
        url = reverse('climate-list')
        data = {'name': 'Polar'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Climate.objects.filter(name='Polar').exists())
    
    def test_climate_planets_action(self):
        """Test custom action to get planets with specific climate"""
        url = reverse('climate-planets', kwargs={'pk': self.climate.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Tropical Planet')


class TerrainViewSetTest(APITestCase):
    """Test TerrainViewSet operations"""
    
    def setUp(self):
        self.client = APIClient()
        self.terrain = Terrain.objects.create(name="Forest")
        self.planet = Planet.objects.create(name="Forest Planet")
        self.planet.terrains.add(self.terrain)
    
    def test_list_terrains(self):
        """Test listing all terrains"""
        url = reverse('terrain-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_terrain(self):
        """Test creating a terrain"""
        url = reverse('terrain-list')
        data = {'name': 'Ocean'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Terrain.objects.filter(name='Ocean').exists())
    
    def test_terrain_planets_action(self):
        """Test custom action to get planets with specific terrain"""
        url = reverse('terrain-planets', kwargs={'pk': self.terrain.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Forest Planet')