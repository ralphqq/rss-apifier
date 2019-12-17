# rss-apifier
This app parses and indexes RSS feeds, so that their entries can be searched and queried via API calls.

## Overview and Features
The app allows you to:

* Register any valid RSS 2.0 feed for parsing
* Index multiple feeds in a single PostgreSQL database backend
* Set schedule and frequency for retrieving newly published entries from feed sources
* Expose the indexed entries via REST API endpoints
* Enable filtering based on different fields (date published, keyword, publisher, etc.) (to be implemented)
* Handle user management [to be implemented]

## Tech Stack and Dependencies

* Python
* Django
* Django Rest Framework
* Celery
* Redis
* PostgreSQL
* Gunicorn
* Nginx
* Docker

## Setup for Development and Deployment
This service can be run directly in your local environment (suitable for development) or as a multi-container Docker app (recommended for production).

### Setting Environment Variables
The app needs the following environment variables set in a `.env` file saved in the project's root directory:

* `SECRET_KEY` - a random string, preferably very long, and very hard to guess
* `POSTGRES_USER` - name of user that owns the app's database
* `POSTGRES_PASSWORD` - password of above user
* `POSTGRES_DB` - name of the database used by the app
* `DB_PORT` - database port number (optional, defaults to 5432)

### Running in Local Environment

1. Create a Postgres database with the same details as specified in your environment variables
2. Create and activate a virtual environment
3. Install the dependencies: `pip install -r requirements.txt`
4. Run the needed migrations: `python manage.py migrate`
5. Create a superuser: `python manage.py createsuperuser`
6. Run the Django development server: `python manage.py runserver`
7. Run a Redis server accessible via port 6379
8. Open new terminal, `cd` into project root, and run a Celery worker: `celery -A rss_apifier worker -l INFO`
9. Open new terminal, `cd` into project root, and run Celery Beat: `celery -A rss_apifier beat -l INFO `--scheduler django_celery_beat.schedulers:DatabaseScheduler

**Notes**:

* See section below on generating an authentication token for admin users
* See section below on adding new feeds
* See section on adding periodic schedules
* The above steps should run the service on `localhost:8000`; try making an API call via curl and check if response is 200: `curl http://localhost:8000/api/entries/`

### Running with Docker

1. Build the images: `docker-compose build`
2. Run the whole app: `docker-compose up`

**Notes:**

* Step two runs the app in a production-ready configuration:
    * gunicorn as app server behind nginx listening on port 80
    * PostgreSQL database, Redis, Celery worker, and Celery Beat in separate containers
    * Django production settings
* Try making an API call with curl: `curl http://localhost/api/entries/`

## Admin and Authentication
To be finanlized

## RSS Feeds and Entries
To be finanlized

## API Reference
To be finanlized