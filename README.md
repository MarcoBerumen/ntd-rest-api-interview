# Planet API - Django REST Framework

A comprehensive Django REST API for managing planets, climates, and terrains with data sourced from the Star Wars API (SWAPI).

## Table of Contents
- [Getting Started](#getting-started)
- [Model Relationships](#model-relationships)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)
- [Running Tests](#running-tests)

## Getting Started

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- Pipenv

### Installation

1. **Start the PostgreSQL Database**
   ```bash
   docker-compose up -d
   ```

2. **Set up the Python environment**
   ```bash
   pipenv shell
   pipenv install
   ```

3. **Run Django setup commands**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Fetch planet data from SWAPI**
   ```bash
   python manage.py fetch_planets
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## Model Relationships

### Data Model Overview

The application uses a normalized data model with three main entities:

```
Planet (1) ←→ (M) Climate
Planet (1) ←→ (M) Terrain
```

### Models

#### Planet
- **name**: Unique planet name (CharField, max 200 chars)
- **population**: Optional population data (CharField, max 50 chars)
- **climates**: Many-to-many relationship with Climate model
- **terrains**: Many-to-many relationship with Terrain model
- **created_at/updated_at**: Automatic timestamps

#### Climate
- **name**: Unique climate name (CharField, max 100 chars)
- **created_at/updated_at**: Automatic timestamps

#### Terrain
- **name**: Unique terrain name (CharField, max 100 chars)
- **created_at/updated_at**: Automatic timestamps

### Key Logic

1. **Data Normalization**: Climates and terrains are stored as separate entities linked via many-to-many relationships, enabling efficient querying and data integrity.

2. **Automatic Creation**: When creating planets via API, climates and terrains are automatically created if they don't exist.

3. **Data Cleaning**: The `fetch_planets` command processes raw SWAPI data, handling unknown values, array parsing, and data validation.

4. **Validation**: Comprehensive validation ensures data quality, including name format validation, duplicate prevention, and relationship limits.

## API Documentation

Please import this collection to postman:
 [Postman Export](./Star%20wars%20api.postman_collection.json)

## Environment Variables

### Required Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DB_NAME=ntd_database
DB_USER=database_user
DB_PASSWORD=database_password
DB_HOST=localhost
DB_PORT=5431
```

### Docker Environment

The `docker-compose.yml` file sets up PostgreSQL with these defaults:
- Database: `ntd_database`
- Username: `database_user`
- Password: `database_password`
- Port: `5431`

## Running Tests

### Setup Test Environment

1. **Install test dependencies:**
   ```bash
   pipenv install --dev
   ```

2. **Install pytest-django (optional):**
   ```bash
   pip install pytest-django pytest-cov
   ```

### Running Tests with Django

**Run all tests:**
```bash
python manage.py test
```

**Run specific test modules:**
```bash
python manage.py test api.tests.test_models
python manage.py test api.tests.test_serializers
python manage.py test api.tests.test_views
python manage.py test api.tests.test_fetch_planets_command
```

### Test Categories

The test suite includes:

- **Model Tests**: Database models, relationships, constraints
- **Serializer Tests**: Data validation, transformation, error handling
- **View Tests**: API endpoints, CRUD operations, filtering
- **Integration Tests**: End-to-end workflows, data consistency
- **Command Tests**: Management command functionality with mocked APIs


<!-- *************************** *** DJANGO CODE CHALLENGE********************** ******** 
Great job on the Django challenge! To help you achieve a perfect score, here are some specific improvements you can work on: 
1. Normalize Data Model for Climate and Terrain • Currently, terrain and climate are stored as comma-separated strings in a TextField. Instead, model them as many-to-many relationships using separate Terrain and Climate models. • This will enable efficient querying (e.g., filter all planets with a certain terrain) and better data integrity. Example: class Terrain(models.Model): name = models.CharField(max_length=100) class Planet(models.Model): ... terrains = models.ManyToManyField(Terrain) ⸻ 

2. Add Retry Logic for External API Calls • In your fetch_planets.py command, wrap your requests with retry logic using requests.adapters or a simple retry loop. • Handle common errors like timeouts, rate limits, or 5xx responses gracefully. • Consider exponential backoff or limiting retry attempts. Resources: tenacity or urllib3.util.retry ⸻ 

3. Implement Unit and Integration Tests • Add test cases for: • Planet model creation and relationships • Serializer validations • API endpoints (CRUD operations) • Management command (mocking the API) • Use Django’s TestCase class and pytest-django if desired. Tools: Django TestCase, DRF test client, unittest.mock ⸻ 

4. Expand Error Handling and Field Validation • In serializers and views, validate inputs and edge cases. • Ensure your API gracefully handles: • Missing or invalid fields • Empty strings or malformed data • Invalid update/delete requests • Return descriptive error messages with appropriate HTTP status codes. ⸻ 

5. Improve the README File • Include: • Example API requests and responses (curl or Postman snippets) • Description of model relationships and key logic • Expected environment variables and default values • Instructions on how to run tests ⸻ 

6. Add Inline Comments and Minor Refactoring • Add comments explaining complex logic (e.g., how data is transformed during import). • Extract helper functions from fetch_planets.py to keep it clean and testable. • Consider introducing services.py for business logic separation. ⸻

 By completing these improvements, you’ll elevate your code to production-level quality and demonstrate mastery of both Django and RESTful principles. -->