from django.test import TestCase, TransactionTestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from ..models import Planet, Climate, Terrain


class PlanetIntegrationTest(APITestCase):
    """Integration tests for complete planet workflows"""
    
    def test_complete_planet_lifecycle(self):
        """Test creating, updating, and deleting a planet with all relationships"""
        # 1. Create a planet with new climates and terrains
        create_url = reverse('planet-list')
        create_data = {
            'name': 'Test Planet',
            'population': '1000000',
            'climates': ['Temperate', 'Humid'],
            'terrains': ['Forest', 'Rivers']
        }
        
        response = self.client.post(create_url, create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        planet_id = response.data['id']
        
        # Verify planet and relationships were created
        self.assertEqual(Planet.objects.count(), 1)
        self.assertEqual(Climate.objects.count(), 2)
        self.assertEqual(Terrain.objects.count(), 2)
        
        planet = Planet.objects.get(id=planet_id)
        self.assertEqual(planet.climates.count(), 2)
        self.assertEqual(planet.terrains.count(), 2)
        
        # 2. Update the planet
        update_url = reverse('planet-detail', kwargs={'pk': planet_id})
        update_data = {
            'name': 'Updated Test Planet',
            'population': '2000000',
            'climates': ['Temperate', 'Arid'],  # Replace Humid with Arid
            'terrains': ['Desert']  # Replace all with Desert
        }
        
        response = self.client.put(update_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify updates
        planet.refresh_from_db()
        self.assertEqual(planet.name, 'Updated Test Planet')
        self.assertEqual(planet.population, '2000000')
        self.assertEqual(planet.climates.count(), 2)
        self.assertEqual(planet.terrains.count(), 1)
        
        # Verify new climate was created
        self.assertTrue(Climate.objects.filter(name='Arid').exists())
        self.assertTrue(Terrain.objects.filter(name='Desert').exists())
        
        # 3. Test custom actions
        climate = Climate.objects.get(name='Temperate')
        climate_planets_url = reverse('climate-planets', kwargs={'pk': climate.pk})
        response = self.client.get(climate_planets_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # 4. Delete the planet
        response = self.client.delete(update_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify planet is deleted but climates/terrains remain
        self.assertEqual(Planet.objects.count(), 0)
        self.assertTrue(Climate.objects.count() > 0)  
        self.assertTrue(Terrain.objects.count() > 0)
    
    def test_concurrent_planet_creation(self):
        """Test that concurrent planet creation handles unique constraints properly"""
        
        create_url = reverse('planet-list')
        data = {
            'name': 'Concurrent Planet',
            'population': '1000'
        }
        
        # First creation should succeed
        response1 = self.client.post(create_url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second creation with same name should fail
        response2 = self.client.post(create_url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        """Test search and filtering capabilities"""
        # Create test data
        planet1 = Planet.objects.create(name="Earth", population="7800000000")
        planet2 = Planet.objects.create(name="Mars", population="0")
        planet3 = Planet.objects.create(name="Venus", population="0")
        
        climate_temp = Climate.objects.create(name="Temperate")
        climate_arid = Climate.objects.create(name="Arid")
        
        planet1.climates.add(climate_temp)
        planet2.climates.add(climate_arid)
        
        list_url = reverse('planet-list')
        
        # Test search
        response = self.client.get(list_url, {'search': 'Earth'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Earth')
        
        # Test ordering
        response = self.client.get(list_url, {'ordering': '-name'})
        names = [planet['name'] for planet in response.data['results']]
        self.assertEqual(names, ['Venus', 'Mars', 'Earth', 'Concurrent Planet'])
        
        # Test search by population
        response = self.client.get(list_url, {'search': '0'})
        self.assertEqual(len(response.data['results']), 4)