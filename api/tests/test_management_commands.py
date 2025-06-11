# test_fetch_planets_command.py
from django.test import TestCase
from django.core.management import call_command
from unittest.mock import patch, Mock, MagicMock
from io import StringIO
import requests
import json
from requests.exceptions import ConnectionError, Timeout, HTTPError, RequestException
from api.models import Planet, Climate, Terrain


class FetchPlanetsCommandTest(TestCase):
    """Test cases for fetch_planets management command"""
    
    def setUp(self):
        """Set up test data"""
        self.mock_api_response = {
            'data': {
                'allPlanets': {
                    'planets': [
                        {
                            'name': 'Tatooine',
                            'population': '200000',
                            'terrains': ['desert'],
                            'climates': ['arid']
                        },
                        {
                            'name': 'Alderaan',
                            'population': '2000000000',
                            'terrains': ['grasslands', 'mountains'],
                            'climates': ['temperate']
                        },
                        {
                            'name': 'Yavin IV',
                            'population': '1000',
                            'terrains': ['jungle', 'rainforests'],
                            'climates': ['temperate', 'tropical']
                        }
                    ]
                }
            }
        }
    
    @patch('requests.Session.get')
    def test_successful_planet_import(self, mock_get):
        """Test successful import of planets from API"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = self.mock_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        out = StringIO()
        call_command('fetch_planets', stdout=out)
        
        # Verify planets were created
        self.assertEqual(Planet.objects.count(), 3)
        self.assertTrue(Planet.objects.filter(name='Tatooine').exists())
        self.assertTrue(Planet.objects.filter(name='Alderaan').exists())
        self.assertTrue(Planet.objects.filter(name='Yavin IV').exists())
        
        # Verify climates were created
        self.assertTrue(Climate.objects.filter(name='arid').exists())
        self.assertTrue(Climate.objects.filter(name='temperate').exists())
        self.assertTrue(Climate.objects.filter(name='tropical').exists())
        
        # Verify terrains were created
        self.assertTrue(Terrain.objects.filter(name='desert').exists())
        self.assertTrue(Terrain.objects.filter(name='grasslands').exists())
        self.assertTrue(Terrain.objects.filter(name='mountains').exists())
        self.assertTrue(Terrain.objects.filter(name='jungle').exists())
        self.assertTrue(Terrain.objects.filter(name='rainforests').exists())
        
        # Verify relationships
        tatooine = Planet.objects.get(name='Tatooine')
        self.assertEqual(tatooine.population, '200000')
        self.assertEqual(tatooine.climates.count(), 1)
        self.assertEqual(tatooine.terrains.count(), 1)
        self.assertTrue(tatooine.climates.filter(name='arid').exists())
        self.assertTrue(tatooine.terrains.filter(name='desert').exists())
        
        yavin = Planet.objects.get(name='Yavin IV')
        self.assertEqual(yavin.climates.count(), 2)
        self.assertEqual(yavin.terrains.count(), 2)
        
        # Check command output
        output = out.getvalue()
        self.assertIn('Retrieved 3 planets', output)
        self.assertIn('Created: Tatooine', output)
        self.assertIn('Created: 3', output)
   