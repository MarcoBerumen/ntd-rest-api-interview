# serializers.py
from rest_framework import serializers
from .models import Climate, Planet, Terrain

class TerrainSerializer(serializers.ModelSerializer):
    """Serializer for Terrain model"""
    
    class Meta:
        model = Terrain
        fields = ['name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ClimateSerializer(serializers.ModelSerializer):
    """Serializer for Climate model"""
    
    class Meta:
        model = Climate
        fields = ['name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class PlanetSerializer(serializers.ModelSerializer):
    """Serializer for Planet model with validation"""

    # Nested serializers for read operations
    terrains = TerrainSerializer(many=True, read_only=True)
    climates = ClimateSerializer(many=True, read_only=True)

     # Use SlugRelatedField to reference by name (the primary key)
    terrain_names = serializers.SlugRelatedField(
        queryset=Terrain.objects.all(),
        many=True,
        slug_field='name',
        source='terrains',
        write_only=True,
        required=False,
        help_text="List of terrain names"
    )
    
    climate_names = serializers.SlugRelatedField(
        queryset=Climate.objects.all(),
        many=True,
        slug_field='name',
        source='climates',
        write_only=True,
        required=False,
        help_text="List of climate names"
    )
    
    class Meta:
        model = Planet
        fields = ['id', 'name', 'population', 'terrains', 'climates', 'created_at', 'updated_at', 'climate_names', 'terrain_names']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """Custom validation for planet name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Planet name must be at least 2 characters long.")
        return value.strip().title()
    
    def create(self, validated_data):
        """Create planet with terrain and climate relationships"""
        terrains = validated_data.pop('terrains', [])
        climates = validated_data.pop('climates', [])
        
        planet = Planet.objects.create(**validated_data)
        
        if terrains:
            planet.terrains.set(terrains)
        if climates:
            planet.climates.set(climates)
            
        return planet

    def update(self, instance, validated_data):
        """Update planet with terrain and climate relationships"""
        terrains = validated_data.pop('terrains', None)
        climates = validated_data.pop('climates', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update relationships if provided
        if terrains is not None:
            instance.terrains.set(terrains)
        if climates is not None:
            instance.climates.set(climates)
            
        return instance


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