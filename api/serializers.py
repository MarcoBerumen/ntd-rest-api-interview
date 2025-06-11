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
    terrains = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Terrain.objects.all(),
        required=False
    )

    climates = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Climate.objects.all(),
        required=False
    )
    class Meta:
        model = Planet
        fields = ['id', 'name', 'population', 'terrains', 'climates']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        climates_data = validated_data.pop('climates', [])
        terrains_data = validated_data.pop('terrains', [])
        planet = Planet.objects.create(**validated_data)
        
        for climate in climates_data:
            planet.climates.add(climate)

        for terrain in terrains_data:
            planet.terrains.add(terrain)
        
        return planet
    
    def update(self, instance, validated_data):
        climates_data = validated_data.pop('climates', None)
        terrains_data = validated_data.pop('terrains', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update climates if provided
        if climates_data is not None:
            instance.climates.clear()  # Remove existing relationships
            for climate in climates_data:
                instance.climates.add(climate)

        if terrains_data is not None:
            instance.terrains.clear()
            for terrain in terrains_data:
                instance.terrains.add(terrain)
        
        return instance
    
    def to_internal_value(self, data):

    
        if 'climates' in data:
            climate_names = data['climates']
            climates = []
            
            for name in climate_names:
                climate, created = Climate.objects.get_or_create(name=name)
                climates.append(climate)
            
            data = data.copy()
            data['climates'] = climates


        if 'terrains' in data:
            terrain_names = data['terrains']
            terrains = []
            
            for name in terrain_names:
                terrain, created = Terrain.objects.get_or_create(name=name)
                terrains.append(terrain)
            
            data = data.copy()
            data['terrains'] = terrains       

        return super().to_internal_value(data)