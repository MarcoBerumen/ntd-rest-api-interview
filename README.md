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