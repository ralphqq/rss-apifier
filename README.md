# rss-apifier

![Build Status](https://github.com/ralphqq/rss-apifier/workflows/ralphqq-rss-apifier-ci/badge.svg)

This app parses and indexes RSS feeds, so that their entries can be searched and queried via API calls.

## Contents

* [Overview and Features](#overview)
* [Tech Stack and Dependencies](#dependencies)
* [Setup and Configuration](#setup)
    * [Setting environment variables](#env-vars)
    * [Running in local environment](#local-env)
    * [Running with Docker](#docker-env)
* [Admin and Authentication](#admin-auth)
    * [Using auth token from default admin user](#admin-auth-default)
    * [Generating/Changing auth tokens via the Site admin page](#admin-auth-page)
    * [Obtaining an auth token via API endpoint](#admin-auth-endpoint)
    * [Generating an auth token in the command line](#admin-auth-cli)
* [RSS Feeds and Entries](#rss-feeds)
    * [Adding and managing RSS feeds](#managing-feeds)
    * [Fetching entries from feeds](#fetching-entries)
* [API Reference](#api-reference)
    * [Resources and Endpoints](#api-reference-endpoints)
    * [Parameters and Requests](#api-reference-params)
    * [Response Schemas](#api-reference-response)
* [Contributing](#contributing)
* [License](#license)

## Overview and Features<a name="overview"></a>
The service allows you to:

* Register any valid RSS 2.0 feed for parsing
* Index multiple feeds in a single PostgreSQL database backend
* Set schedule and frequency for retrieving newly published entries from feed sources
* Expose the indexed entries via REST API endpoints
* Enable filtering based on different fields (date published, keyword, publisher, etc.) (to be implemented)
* Handle user management and permiessions/authentication

## Tech Stack and Dependencies<a name="dependencies"></a>
The app needs the following things to work:

* Python 3.6
* Django
* Django Rest Framework
* feedparser
* Celery
* Redis
* PostgreSQL
* Gunicorn
* Nginx
* Docker

## Setup and Configuration<a name="setup"></a>
This service can be run directly in your local environment (suitable for development) or as a multi-container Docker app (recommended for production).

### Setting environment variables<a name="env-vars"></a>
The app needs the following environment variables set in a `.env` file in the project's root directory:

* `SECRET_KEY` - a random string, preferably very long, and very hard to guess
* `POSTGRES_USER` - name of user that owns the app's database
* `POSTGRES_PASSWORD` - password of above user
* `POSTGRES_DB` - name of the database used by the app
* `DB_PORT` - database port number (optional, defaults to 5432)
* `ADMIN_USER` - username of default admin user (optional)
* `ADMIN_PASSWORD` - password of default admin user (optional)
* `ADMIN_EMAIL` - email address of default admin user (optional)

### Running in local environment<a name="local-env"></a>

1. Create a Postgres database with the same details as specified in your environment variables
2. Create and activate a virtual environment
3. Install the development dependencies:
    ```console
    $ pip install -r requirements.txt
    ```
4. Run the needed migrations:
    ```console
    $ python manage.py migrate
    ```
5. Create a superuser:
    ```console
    $ python manage.py createsuperuser
    ```
6. Check if setup is ok:
    ```console
    $ pytest
    ```
7. Run the Django development server:
    ```console
    $ python manage.py runserver
    ```
8. Run a Redis server accessible via port 6379
9. Open a new terminal, `cd` into project root, and run a Celery worker:
    ```console
    $ celery -A rss_apifier worker -l INFO
    ```
10. Open a new terminal, `cd` into project root, and run Celery Beat:
    ```console
    $ celery -A rss_apifier beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
    ```

**Notes**:

* The above steps should run the service on `localhost:8000`; try making an API call via curl and check if response is 200: `curl http://localhost:8000/api/entries/`
* See section below on [generating an authentication token for admin users](#admin-auth)
* See section below on [adding new feeds](#managing-feeds)
* See section on [configuring periodic schedules](#fetching-entries)

### Running with Docker<a name="docker-env"></a>

1. Build the images:
    ```console
    $ docker-compose build
    ```
2. Run the whole app:
    ```console
    $ docker-compose up
    ```

**Notes:**

* Step two runs the app in a production-ready configuration:
    * gunicorn as app server behind nginx listening on port 80
    * PostgreSQL database, Redis, Celery worker, and Celery Beat in separate containers
    * Django production settings
* Try making an API call with curl: `curl http://localhost/api/entries/`

## Admin and Authentication<a name="admin-auth"></a>
In order to add, modify, and delete RSS feeds, a user needs to have admin privileges and must be authenticated with a token. The app provides several ways to obtain these requirements:

### Using auth token from default admin user<a name="admin-auth-default"></a>
When launching the app through Docker (using the `docker-compose.yml` file in the root directory), a default admin user and auth token will be created based on the values of the environment variables `ADMIN_USER`, `ADMIN_PASSWORD`, and `ADMIN_EMAIL`. The default admin user and token will be created only if all three variables have valid values.
When running the app directly on your local environment, however, the default admin user will not be created automatically, so you need to create this yourself and then follow the instructions in the next sections to generate an auth token.

### Generating/Changing auth tokens via the Site admin page<a name="admin-auth-page"></a>
The Site administration page (available via `hostname/admin`) allows you to set and change auth tokens for any valid user.

`. Log on to the Site admin page
2. Click 'Add' under the `AUTH TOKEN` table
3. Choose the user you want to generate an auth token for
4. Click 'Save'

**Notes:**

* The above steps require a user with `superuser` privileges.
* The steps are similar to how you change a user's existing auth token.

### Obtaining an auth token via API endpoint<a name="admin-auth-endpoint"></a>
The app also exposes an API endpoint for obtaining an existing user's current auth token via the following URL:

```
/accounts/token/
```

**Notes:**

* The endpoint accets post requests only and expects a JSON payload that contains `{"username": "some_username", "password": "some_password"}`.
* If user credentials are valid, the endpoint returns a JSON object that contains `{"token": "SOMEAUTH_TOKEN"}`.
* The endpoint generates a new auth token if the user currently doesn't have one yet.
* For more, see the section on [obtaining an auth token via API endpoint](#endpoints-account-token)

### Generating an auth token in the command line<a name="admin-auth-cli"></a>
Another way to generate an auth token for a user is to use DRF's custom management command:

```console
$ python manage.py drf_create_token NAME_OF_SUPERUSER
```

## RSS Feeds and Entries<a name="rss-feeds"></a>
The app ships with several features for easily managing feeds and entries, as well as setting schedules for fetching and updating newly published items.

### Adding and managing RSS feeds<a name="managing-feeds"></a>
Only admin users with the appropriate authentication token can add, view, edit, and delete RSS feeds. These requirements can be obtained through the following:

* **The `Feeds` table on the Site admin page:** To add an RSS feed, you need to provide only the feed's URL. The app automatically fetches a feed's details (e.g., name, description, RSS version, etc.) once you hit the 'Save' button. You can also edit a feed's details or delete a feed altogether on the Site admin page.
* **Various API endpoints:** The app exposes a number of API endpoints for admin users to manage feeds. (see the [Feed section](#endpoints-feed) under API Reference for more)

### Fetching entries from feeds<a name="fetching-entries"></a>
The app automatically fetches, parses, and saves new entries from each registered RSS feed. To control how often to check feeds for newly published items, please do the following steps:

1. Log in to the Site admin page
2. Click 'Add' on either the `Crontabs` or `Intervals` row of the `PERIODIC TASKS` table
3. Specify the values you want for your task schedule and hit 'Save'
4. Go back to the `PERIODIC TASKS` table and click 'Add' on the `Periodic tasks` row
5. Enter an appropriate name for the scheduled task, then choose 'fetch-entries' from the 'Task' dropdown menu
6. Choose the schedule you created in step 2 from either the 'Interval Schedule' or 'Crontab Schedule' dropdown menu
7. Specify values in the other fields as appropriate and click 'Save'

**Note:** For more on managing periodic tasks, see [https://github.com/celery/django-celery-beat](#https://github.com/celery/django-celery-beat)

## API Reference<a name="api-reference"></a>
This section gives a brief overview on the service's API endpoints, requests, and responses.

### Resources and Endpoints<a name="api-reference-params"></a>
The service exposes API endpoints for interacting with saved RSS feeds, indexed feed entries, and registered users. Here's a brief rundown of these endpoints organized by resource.

#### Entry<a name="endpoints-entry"></a>
Contains details associated with a published news article, blog post, or other content. Details include link, title, summary, and published date.

##### Retrieve all feed entries<a name="endpoints-entry-list"></a>
**Description:**  
Retrieves all feed entries currently on record

**Endpoint:**  
`GET /api/entries/`

**Path Parameters:**  
None

**Query Parameters:**  
See section [Query parameters for endpoints that return paginated results](#query-params-paginated)

**Data Parameters:**  
None

**Success Response:**  

* Status Code: 200
* Content: See section [Response body for endpoints that return paginated results>](#response-paginated)

#### Feed<a name="endpoints-feed"></a>
Contains information about a saved RSS feed such as title, description, link, RSS version, etc.

##### Retrieve all saved RSS feeds<a name="endpoints-feed-list"></a>
**Description:**  
Retrieves all RSS feeds on record

**Endpoint:**  
`GET /api/feeds/`

**Path Parameters:**  
None

**Query Parameters:**  
See section [Query parameters for endpoints that return paginated results](#query-params-paginated)

**Data Parameters:**  
None

**Request Headers:**
See section [Request header for endpoints that require authentication](#request-auth-token)

**Success Response:**  

* Status Code: 200
* Content: See section [Response body for endpoints that return paginated results>](#response-paginated)

##### Retrieve a single RSS feed<a name="endpoints-feed-detail"></a>
**Description:**  
Retrieves a single RSS feed using the feed's ID

**Endpoint:**  
`GET /api/feeds/{feed_id}/`

**Path Parameters:**  

* `feed_id` (integer): the feed's unique ID (required)

**Query Parameters:**  
None

**Data Parameters:**  
None

**Request Headers:**
See [Request header for endpoints that require authentication](#request-auth-token)

**Success Response:**  

* Status Code: 200 OK
* Content: See section [Feed objects in response content](#feed-json-obj)

##### Add a new RSS feed<a name="endpoints-feed-create"></a>
**Description:**  
Saves a new RSS feed object into the database

**Endpoint:**  
`POST /api/feeds/`

**Path Parameters:**  
None

**Query Parameters:**  
None

**Data Parameters:**  
This endpoint expects a JSON payload with the following fields/values:
* `link` (string): URL that points to the RSS feed (required), maximum of 400 characters
* `title` (string): the feed's title (optional), maximum of 1,024 characters
* `description` (string): the feed's description (optional), maximum of 2,048 characters

**Request Headers:**
See [Request header for endpoints that require authentication](#request-auth-token)

**Success Response:**  

* Status Code: 201 CREATED
* Content: See section [Feed objects in response content](#feed-json-obj)

##### Modify an existing RSS feed<a name="endpoints-feed-update"></a>
**Description:**  
Changes or updates details of a particular feed

**Endpoint:**  
`PUT /api/feeds/{feed_id}/`

**Path Parameters:**  

* `feed_id` (integer): the feed's unique ID (required)

**Query Parameters:**  
None

**Data Parameters:**  
This endpoint expects a JSON payload with the following fields/values:
* `link` (string): URL that points to the RSS feed (required), maximum of 400 characters
* `title` (string): the feed's title (optional), maximum of 1,024 characters
* `description` (string): the feed's description (optional), maximum of 2,048 characters

**Request Headers:**
See [Request header for endpoints that require authentication](#request-auth-token)

**Success Response:**  

* Status Code: 200
* Content: See section [Feed objects in response content](#feed-json-obj)

##### Delete an existing RSS feed<a name="endpoints-feed-delete"></a>
**Description:**  
Removes a saved RSS feed from the database

**Endpoint:**  
`DELETE /api/feeds/{feed_id}/`

**Path Parameters:**  

* `feed_id` (integer): the feed's unique ID (required)

**Query Parameters:**  
None

**Data Parameters:**  
None

**Request Headers:**
See [Request header for endpoints that require authentication](#request-auth-token)

**Success Response:**  

* Status Code: 204
* Content: None

##### Retrieve all entries from a specific RSS feed<a name="endpoints-feed-entries"></a>
**Description:**  
Retrieves all entries associated with a given RSS feed

**Endpoint:**  
`GET /api/feeds/{feed_id}/entries/`

**Path Parameters:**  

* `feed_id` (integer): the feed's unique ID (required)

**Query parameters:**  
See section [Query parameters for endpoints that return paginated results](#query-params-paginated)

**Data parameters:**  
None

**Request Headers:**
See [Request header for endpoints that require authentication](#request-auth-token)

**Success Response:**  

* Status Code: 200
* Content: See section [Response body for endpoints that return paginated results>](#response-paginated)

#### Account<a name="enddpoints-account"></a>
Includes information on users, permissions, and authentication details

##### Obtain authentication token for a user<a name="endpoints-account-token"></a>
**Description:**  
Obtains a user's current auth key or creates a new one if it doesn't already exist

**Endpoint:**  
`POST /api/accounts/token/`

**Path Parameters:**  
None

**Query Parameters:**  
None

**Data Parameters:**  
This endpoint expects a JSON payload with the following fields/values:
* `username`
* `password`

**Success Response:**  

* Status Code: 200
* Content: JSON object with field `token`

## Parameters and Requests<a name="api-reference-params"></a>
This section dives into some parameters and request attributes common to all (if not most) of the service's API endpoints.

#### Query parameters for endpoints that return paginated results<a name="query-params-paginated"></a>
By default, all endpoints that fetch a collection of objects automatically paginate their results. This behavior can be controlled with the following query parameters:
* `page` (integer): the results page number to return (optional)
* `page_size` (integer): the number of entries per page to return (optional, defaults to 100)

#### Request header for endpoints that require authentication<a name="request-auth-token"></a>
All API endpoints that interact with feed objects require authentication. These endpoints expect the user's auth token to be included in the request header as follows:
```
Authorization: Token 705cf7xa9303e013b3c2300408c3dpd6390qcwdf
```

### Response Schemas<a name="api-reference-response"></a>
This section goes over some response content and schemas returned by most of the service's API endpoints.

#### Response body for endpoints that return paginated results<a name="response-paginated"></a>
API endpoints that return paginated results have the following JSON response content:
* `count`: total number of items found
* `next`: URL to next results page
* `previous`: URL to previous results page
* `results`: array of objects; this can either be an array of [feed objects](#feed-json-obj) or array of [entry objects](#entry-json-obj)

#### Entry objects in response content<a name="entry-json-obj">
A feed entry is represented by the following JSON object:
* `link`: URL to the article/blog post/content
* `title`: the entry's title
* `summary`: the entry's summary
* `published`: ISO-formatted datetime string

#### Feed objects in response content<a name="feed-json-obj"></a>
An RSS feed is represented by the following JSON object:
* `id`: the feed's ID
* `title`: the feed's title
* `description`: the feed's description
* `link`: URL that points to the RSS feed
* `version`: the feed's RSS version
* `entries_count`: the total number of entries associated with this feeed
* `entries_list`: URL that points to the list of entries associated with this feed

## Contributing<a name="contributing"></a>
1. Fork this repo at https://github.com/ralphqq/rss-apifier
2. Clone your fork into your local machine
3. Follow steps in development setup
4. Create your feature branch:
    ```console
    $ git checkout -b feature/some-new-thing
    ```
5. Commit your changes:
    ```console
    $ git commit -m "Develop new thing"
    ```
6. Push to the branch:
    ```console
    $ git push origin feature/some-new-thing
    ```
7. Create a pull request

## License<a name="license"></a>
[MIT license](https://opensource.org/licenses/MIT)
