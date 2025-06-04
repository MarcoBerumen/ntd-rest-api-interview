# serializers.py
from rest_framework import serializers
from .models import Planet

class PlanetSerializer(serializers.ModelSerializer):
    """Serializer for Planet model with validation"""
    
    class Meta:
        model = Planet
        fields = ['id', 'name', 'population', 'terrains', 'climates', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """Custom validation for planet name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Planet name must be at least 2 characters long.")
        return value.strip().title()
    
    def validate_terrains(self, value):
        """Validate terrains is a list of strings"""
        if value is not None and not isinstance(value, list):
            raise serializers.ValidationError("Terrains must be a list of strings.")
        if value is not None:
            for terrain in value:
                if not isinstance(terrain, str):
                    raise serializers.ValidationError("Each terrain must be a string.")
        return value
    
    def validate_climates(self, value):
        """Validate climates is a list of strings"""
        if value is not None and not isinstance(value, list):
            raise serializers.ValidationError("Climates must be a list of strings.")
        if value is not None:
            for climate in value:
                if not isinstance(climate, str):
                    raise serializers.ValidationError("Each climate must be a string.")
        return value


    """Test cases for Planet API"""
    
    def setUp(self):
        self.planet_data = {
            'name': 'Earth',
            'population': '7.8 billion',
            'terrains': ['ocean', 'grassland', 'desert'],
            'climates': ['temperate', 'tropical']
        }
        self.planet = Planet.objects.create(**self.planet_data)
    
    def test_create_planet(self):
        """Test creating a new planet"""
        url = reverse('planet-list')
        data = {
            'name': 'Mars',
            'population': '0',
            'terrains': ['desert'],
            'climates': ['arid']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Planet.objects.count(), 2)
    
    def test_get_planet_list(self):
        """Test retrieving planet list"""
        url = reverse('planet-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_planet_detail(self):
        """Test retrieving a specific planet"""
        url = reverse('planet-detail', kwargs={'pk': self.planet.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Earth')
    
    def test_update_planet(self):
        """Test updating a planet"""
        url = reverse('planet-detail', kwargs={'pk': self.planet.pk})
        data = {'population': '8 billion'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.planet.refresh_from_db()
        self.assertEqual(self.planet.population, '8 billion')
    
    def test_delete_planet(self):
        """Test deleting a planet"""
        url = reverse('planet-detail', kwargs={'pk': self.planet.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Planet.objects.count(), 0)
    
    def test_search_planets(self):
        """Test searching planets"""
        url = reverse('planet-list')
        response = self.client.get(url, {'search': 'Earth'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_by_terrain(self):
        """Test custom terrain filter endpoint"""
        url = reverse('planet-by-terrain')
        response = self.client.get(url, {'terrain': 'ocean'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_duplicate_name_validation(self):
        """Test that duplicate planet names are not allowed"""
        url = reverse('planet-list')
        data = self.planet_data.copy()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)