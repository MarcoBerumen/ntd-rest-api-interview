# serializers.py
from rest_framework import serializers
from .models import Climate, Planet, Terrain
import re

class TerrainSerializer(serializers.ModelSerializer):
    """Serializer for Terrain model"""

    name = serializers.CharField(
        max_length=100,
        min_length=2,
        help_text="Terrain name (2-100 characters)",
        error_messages={
            'required': 'Terrain name is required.',
            'blank': 'Terrain name cannot be empty.',
            'min_length': 'Terrain name must be at least 2 characters long.',
            'max_length': 'Terrain name cannot exceed 100 characters.',
        }
    )
    class Meta:
        model = Terrain
        fields = ['name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_name(self, value):
            """Custom validation for terrain name"""
            if not value or not value.strip():
                raise serializers.ValidationError("Terrain name cannot be empty or whitespace only.")
            
            # Clean the name
            cleaned_name = value.strip()
            
            # Check for invalid characters (allow letters, numbers, spaces, hyphens, apostrophes)
            if not re.match(r"^[a-zA-Z0-9\s\-']+$", cleaned_name):
                raise serializers.ValidationError(
                    "Terrain name can only contain letters, numbers, spaces, hyphens, and apostrophes."
                )
            
            # Check for reserved words
            reserved_words = ['unknown', 'null', 'undefined', 'none']
            if cleaned_name.lower() in reserved_words:
                raise serializers.ValidationError(f"'{cleaned_name}' is a reserved word and cannot be used.")
            
            return cleaned_name

class ClimateSerializer(serializers.ModelSerializer):
    """Serializer for Climate model"""

    name = serializers.CharField(
        max_length=100,
        min_length=2,
        help_text="Climate name (2-100 characters)",
        error_messages={
            'required': 'Climate name is required.',
            'blank': 'Climate name cannot be empty.',
            'min_length': 'Climate name must be at least 2 characters long.',
            'max_length': 'Climate name cannot exceed 100 characters.',
        }
    )
    class Meta:
        model = Climate
        fields = ['name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_name(self, value):
        """Custom validation for climate name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Climate name cannot be empty or whitespace only.")
        
        # Clean the name
        cleaned_name = value.strip()
        
        # Check for invalid characters
        if not re.match(r"^[a-zA-Z0-9\s\-'&/]+$", cleaned_name):
            raise serializers.ValidationError(
                "Climate name can only contain letters, numbers, spaces, hyphens, apostrophes, ampersands, and slashes."
            )
        
        # Check for reserved words
        reserved_words = ['unknown', 'null', 'undefined', 'none']
        if cleaned_name.lower() in reserved_words:
            raise serializers.ValidationError(f"'{cleaned_name}' is a reserved word and cannot be used.")
        
        return cleaned_name

class PlanetSerializer(serializers.ModelSerializer):
    """Serializer for Planet model with validation"""
    name = serializers.CharField(
        max_length=200,
        min_length=2,
        help_text="Planet name (2-200 characters)",
        error_messages={
            'required': 'Planet name is required.',
            'blank': 'Planet name cannot be empty.',
            'min_length': 'Planet name must be at least 2 characters long.',
            'max_length': 'Planet name cannot exceed 200 characters.',
        }
    )
    
    population = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Planet population (optional, max 50 characters)",
        error_messages={
            'max_length': 'Population cannot exceed 50 characters.',
        }
    )

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