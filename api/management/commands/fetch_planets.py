from django.core.management.base import BaseCommand
from django.db import transaction
import requests
import json
import random
import time

import requests.adapters
from api.models import Climate, Planet, Terrain
from urllib3.util.retry import Retry

class Command(BaseCommand):
    help = 'Fetch planets data from SWAPI GraphQL and store in database'
    
    def add_arguments(self, parser):

        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing planets instead of skipping them',
        )

        parser.add_argument(
            '--max-retries',
            type=int,
            default=3,
            help='Maximum number of retries for network requests (default: 3)'
        )

        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Timeout for network requests in seconds (default: 30)'
        )
    
    def handle(self, *args, **options):
        graphql_url = "https://swapi-graphql.netlify.app/graphql?query=query+Query+%7BallPlanets%7Bplanets%7Bname+population+terrains+climates%7D%7D%7D"
        
        try:
            self.stdout.write("Fetching planets data from SWAPI GraphQL...")
            
            # Make GraphQL request
            data = self._make_request_with_retry(
                url=graphql_url,
                retries=options['max_retries'],
                timeout=options['timeout']
            )

            if not data:
                self.stdout.write(self.style.ERROR("Failed to fetch data after all retry attempts"))
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
                        self._set_planet_relationships(planet, planet_data)
                    elif options['update']:
                        # Update existing planet
                        for field, value in self._prepare_planet_data(planet_data).items():
                            setattr(planet, field, value)
                        planet.save()
                        self._set_planet_relationships(planet, planet_data)
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

    def _make_request_with_retry(self, url, retries=3, timeout=30):

        session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )

        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        for attempt in range(retries + 1):
            try:
                self.stdout.write(f"Attempt {attempt + 1}/{retries + 1}...")

                response = session.get(
                    url=url,
                    timeout=timeout,
                    headers={'Content-Type': 'application/json'},
                )

                response.raise_for_status()

                data = response.json()

                if 'errors' in data:
                    error_msg = f"GraphQL errors: {data['errors']}"
                    if attempt < retries:
                        self.stdout.write(self.style.WARNING(error_msg))
                        self._wait_with_backoff(attempt)
                        continue
                    else:
                        raise Exception(error_msg)
                    
                self.stdout.write(self.style.SUCCESS("Request successful!"))
                return data
            
            except requests.exceptions.Timeout as e:
                error_msg = f"Request timed out after {timeout} seconds."
                self._handle_retry_error(error_msg, attempt, retries, e)

            except requests.exceptions.ConnectionError as e:
                error_msg = "Connection error occurred."
                self._handle_retry_error(error_msg, attempt, retries, e)

            except requests.exceptions.HTTPError as e:
                error_msg = f"HTTP error occurred: {e.response.status_code} - {e.response.reason}"
                self._handle_retry_error(error_msg, attempt, retries, e)

            except requests.exceptions.RequestException as e:
                error_msg = f"An error occurred: {str(e)}"
                self._handle_retry_error(error_msg, attempt, retries, e)

            except json.JSONDecodeError as e:
                error_msg = "Failed to decode JSON response."
                self._handle_retry_error(error_msg, attempt, retries, e)

            except Exception as e:
                error_msg = f"An unexpected error occurred: {str(e)}"
                self._handle_retry_error(error_msg, attempt, retries, e)

        return None
    
    def _prepare_planet_data(self, planet_data):
        """Prepare planet data for database storage"""
        return {
            'population': self._clean_field(planet_data.get('population'))
        }
    
    def _set_planet_relationships(self, planet, planet_data):

        terrains = self._process_array_field(planet_data.get('terrains'))
        if terrains:
            terrain_objects = []
            for terrain_name in terrains:
                terrain, _ = Terrain.objects.get_or_create(name=terrain_name)
                terrain_objects.append(terrain)
            planet.terrains.set(terrain_objects)

        climates = self._process_array_field(planet_data.get('climates'))
        if climates:
            climate_objects = []
            for climate_name in climates:
                climate, _ = Climate.objects.get_or_create(name=climate_name)
                climate_objects.append(climate)
            planet.climates.set(climate_objects)
    
    def _clean_field(self, value):
        """Clean and validate field values"""
        if value is None or value == 'unknown' or value == 'n/a':
            return None
        return str(value).strip()
    
    def _wait_with_backoff(self, attempt):
        wait_time = (2 ** attempt) + random.uniform(0.1, 0.5)  # Exponential backoff
        self.stdout.write(self.style.WARNING(f"Attempt {attempt}. Waiting {wait_time:.2f} seconds before retrying..."))
        time.sleep(wait_time)

    def _handle_retry_error(self, error_msg, attempt, retries, exception):
        if attempt < retries:
            self.stdout.write(self.style.WARNING(f"Error: {error_msg}. Retrying..."))
            self._wait_with_backoff(attempt)
        else:
            self.stdout.write(self.style.ERROR(f"Max retries reached. Last error: {error_msg}"))
            raise exception
    
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