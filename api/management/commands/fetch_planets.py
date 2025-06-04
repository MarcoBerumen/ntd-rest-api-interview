from django.core.management.base import BaseCommand
from django.db import transaction
import requests
import json
from api.models import Planet

class Command(BaseCommand):
    help = 'Fetch planets data from SWAPI GraphQL and store in database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing planets instead of skipping them',
        )
    
    def handle(self, *args, **options):
        graphql_url = "https://swapi-graphql.netlify.app/graphql?query=query+Query+%7BallPlanets%7Bplanets%7Bname+population+terrains+climates%7D%7D%7D"
        
        try:
            self.stdout.write("Fetching planets data from SWAPI GraphQL...")
            
            # Make GraphQL request
            response = requests.get(
                graphql_url,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'errors' in data:
                self.stdout.write(
                    self.style.ERROR(f"GraphQL errors: {data['errors']}")
                )
                return
            
            planets_data = data['data']['allPlanets']['planets']
            self.stdout.write(f"Retrieved {len(planets_data)} planets")
            
            # Process and save planets
            created_count = 0
            updated_count = 0
            skipped_count = 0
            
            with transaction.atomic():
                for planet_data in planets_data:
                    planet_name = planet_data.get('name', '').strip()
                    
                    if not planet_name or planet_name.lower() == 'unknown':
                        skipped_count += 1
                        continue
                    
                    # Check if planet exists
                    planet, created = Planet.objects.get_or_create(
                        name=planet_name,
                        defaults=self._prepare_planet_data(planet_data)
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(f"Created: {planet_name}")
                    elif options['update']:
                        # Update existing planet
                        for field, value in self._prepare_planet_data(planet_data).items():
                            setattr(planet, field, value)
                        planet.save()
                        updated_count += 1
                        self.stdout.write(f"Updated: {planet_name}")
                    else:
                        skipped_count += 1
            
            # Print summary
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSummary:\n"
                    f"Created: {created_count}\n"
                    f"Updated: {updated_count}\n"
                    f"Skipped: {skipped_count}\n"
                    f"Total processed: {len(planets_data)}"
                )
            )
            
        except requests.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f"Network error: {e}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Unexpected error: {e}")
            )
    
    def _prepare_planet_data(self, planet_data):
        """Prepare planet data for database storage"""
        return {
            'population': self._clean_field(planet_data.get('population')),
            'terrains': self._process_array_field(planet_data.get('terrains')),
            'climates': self._process_array_field(planet_data.get('climates'))
        }
    
    def _clean_field(self, value):
        """Clean and validate field values"""
        if value is None or value == 'unknown' or value == 'n/a':
            return None
        return str(value).strip()
    
    def _process_array_field(self, value):
        """Process array fields (terrains, climates)"""
        if not value or value == 'unknown':
            return None
        
        # If it's already a list, return it
        if isinstance(value, list):
            return [item.strip() for item in value if item and item.strip()]
        
        # If it's a string, try to split it
        if isinstance(value, str):
            # Split by common delimiters
            items = []
            for delimiter in [',', ';', '|']:
                if delimiter in value:
                    items = [item.strip() for item in value.split(delimiter)]
                    break
            else:
                items = [value.strip()]
            
            return [item for item in items if item and item != 'unknown']
        
        return None