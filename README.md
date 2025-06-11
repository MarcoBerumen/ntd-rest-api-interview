### GET STARTED

Start the docker Postgres Database

```sh
    docker-compose up -d
```

Make migrations, create super user, fetch planets and start server.
```sh
pipenv shell

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

python manage.py fetch_planets
python manage.py runserver


```

*************************** *** DJANGO CODE CHALLENGE********************** ******** 
Great job on the Django challenge! To help you achieve a perfect score, here are some specific improvements you can work on: 
1. Normalize Data Model for Climate and Terrain • Currently, terrain and climate are stored as comma-separated strings in a TextField. Instead, model them as many-to-many relationships using separate Terrain and Climate models. • This will enable efficient querying (e.g., filter all planets with a certain terrain) and better data integrity. Example: class Terrain(models.Model): name = models.CharField(max_length=100) class Planet(models.Model): ... terrains = models.ManyToManyField(Terrain) ⸻ 

2. Add Retry Logic for External API Calls • In your fetch_planets.py command, wrap your requests with retry logic using requests.adapters or a simple retry loop. • Handle common errors like timeouts, rate limits, or 5xx responses gracefully. • Consider exponential backoff or limiting retry attempts. Resources: tenacity or urllib3.util.retry ⸻ 

3. Implement Unit and Integration Tests • Add test cases for: • Planet model creation and relationships • Serializer validations • API endpoints (CRUD operations) • Management command (mocking the API) • Use Django’s TestCase class and pytest-django if desired. Tools: Django TestCase, DRF test client, unittest.mock ⸻ 

4. Expand Error Handling and Field Validation • In serializers and views, validate inputs and edge cases. • Ensure your API gracefully handles: • Missing or invalid fields • Empty strings or malformed data • Invalid update/delete requests • Return descriptive error messages with appropriate HTTP status codes. ⸻ 

5. Improve the README File • Include: • Example API requests and responses (curl or Postman snippets) • Description of model relationships and key logic • Expected environment variables and default values • Instructions on how to run tests ⸻ 

6. Add Inline Comments and Minor Refactoring • Add comments explaining complex logic (e.g., how data is transformed during import). • Extract helper functions from fetch_planets.py to keep it clean and testable. • Consider introducing services.py for business logic separation. ⸻

 By completing these improvements, you’ll elevate your code to production-level quality and demonstrate mastery of both Django and RESTful principles.