# Job Offers REST API

A Simple API for job offers built with Flask restplus Framework and Postgres database.

## Quick start

### Prerequisites

In order to run the project in a local environment, all you need is Docker and docker-compose tool installed.
You may also want to have `pipenv` tool installed to run the project in a virtual environment

### Building the project

Go to the project directory where `docker-compose.yaml` and `Dockerfile` are located and run the command:

```bash
$ docker-compose build
```

### Running the project with Docker

```bash
$ docker-compose up -d postgres
$ docker-compose up
```

> **Note**: When running the project for the first time, make sure to run the `postgres` container first then run the `api` container. running `docker-compose up` will cause the application to crash since the database is not ready to accept connetions.

### Running the project with a virtual environment

After activating the `virtualenv`:

```bash
$ pip install -r requirements.txt
$ ./script/runserver.sh
```

The script will run the database instance with docker and start the server.


### Running the tests

Tests use a real database to make the testing environment similar to production, also note that some database features such as `string array` are not available for sqlite.

To run tests use the script:

```bash
$ ./script/test.sh
```

## Project Details

### Context

The main objective of this mini-project is to walk through some important concepts of building REST APIs that are used in any framework (Flask, Symfony, .net core...) which are :
- Views : Process incoming requests and return responses
- Models : contain the essential fields and behaviors of the data being stored.
- Authentication & permissions classes: define and restrict access to the API resources.
- Deployment using docker & Kubernets.

### Goal

In this project, the task is to implement a simple API that stores the users’ job offers, so each can create/modify/delete their own offers and can view the others one. The project consist of a simple model that have the following fields :
- title : the title of the job offer (cannot be null)
- description : the description of the job offer
- skills_list : a list of required skills
- creation_date : datetime type
- modification_date : datetime type (should be null if no modification was performed)

### Main Endpoints

- POST /users/<id>/offers : allow the user to create an offer
- GET /users/<id>/offers : allow the user to list all offers of a specific user
- GET /users/<id>/offers/<id> : allow the user to retrieve an offer
- PUT /users/<id>/offers/<id> : allow the user to modify an existing offer
- DELETE /users/<id>/offers/<id> : allow the user to delete an offer

### Authentication

Before a user can perform any action to the api, he/she must be authenticated,
which means he already have an account and provided the necessary credentials to access
the api.

### Permission

- A user can create, view, update and delete his own offers.
- A user can only view other offers.

### Project structure

```
├── api                             #   Api main directory
│   ├── auth.py                     #   Python decorator for API tokens authentication 
│   ├── db.py                       #   
│   ├── __init__.py                 #  
│   ├── models.py                   #   Models definition
│   ├── resources.py                #   Namespaces and Resources definitions
│   └── schemas.py                  #   Serialization Deserialization classes
├── app.py                          #   Main flask application file
├── config.py                       #   Settings definition for each environment
├── docker-compose.yml              #  
├── Dockerfile                      #  
├── manage.py                       #   Script for managing migrations
├── migrations                      #   Alembic autogenerated migration files
├── postgres.yml                    #   Test database
├── README.md                       #  
├── .gitlab-ci.yml                  #   Gitlab CI/CD pipeline
├── requirements.txt                #
├── tests.py                        #   TestCase classes for integration tests 
├── scripts                         #  
│   ├── runserver.sh                #   Script for running the server locally using database container
│   └── test.sh                     #   Script for running tests using containarized test database
├── chart                           #   Helm chart for kubernetes deployment
│   ├── Chart.yaml                  #  
│   ├── templates                   #   .yaml files for kubernetes objects
│   │   ├── api-configmap.yaml      #   configmap to store the whole deployment configuration
│   │   ├── deployment.yaml         #   Api deployment object definition
│   │   ├── _helpers.tpl            #  
│   │   ├── ingress.yaml            #   Ingress for external access to the application
│   │   ├── NOTES.txt               #  
│   │   ├── postgres.yaml           #   Postgres deployment, service and volume
│   │   └── service.yaml            #   Kubernetes service for api access
│   └── values.yaml                 #   chart values
└── wsgi.py                         #   Uwsgi server initialization
```

### Main packages used:

 - Flask-restplus - Flask REST Framework.
 - SQLAlchemy - ORM for database operations.
 - Marshmallow - Serialization/Deserialization package.
 - PyJWT - JSON Web Token implementation.
 - Flask-Migrate - database migrations handeling.
 - Flask-Script - provides support for writing external scripts.

### API endpoints testing with curl

#### Users

This endpoint is used for users registration and login.

- Registration `curl` commad:

```bash
curl -X POST "http://localhost:5000/api/v1/users/register" -H "accept: application/json" -H"Content-Type: application/json" -d "{ \"username\": \"user\", \"password\": \"password\"}"
# Response
{
  "username": "user",
  "id": 1
}
 ```
- Login `curl` commad:
```bash
curl -X POST "http://localhost:5000/api/v1/users/login" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"username\": \"user\", \"password\": \"password\"}"
# Response
{
  "id": 1,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJ1c2VyIiwiZXhwaXJlc19hdCI6IjIwMTgtMTAtMjMgMjE6NTM6NDMuODA0MjEyIn0.DIMHTfqqU-SDVW_kLXukh0pc9MOtO7uyvw4oIbXxtL4"
}
```

#### Offers

This endpoint is for CRUD operations for job offers. it requires token authentication.

- Create a job offer

```bash
curl -X POST "http://localhost:5000/api/v1/users/1/offers/" -H "accept: application/json" -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJ1c2VyIiwiZXhwaXJlc19hdCI6IjIwMTgtMTAtMjMgMjE6NTM6NDMuODA0MjEyIn0.DIMHTfqqU-SDVW_kLXukh0pc9MOtO7uyvw4oIbXxtL4" -H "Content-Type: application/json" -d "{ \"title\": \"Backend Engineer\", \"description\": \"Build a RESTful API\", \"skills_list\": [\"python\", \"flask\", \"DevOps\"]}"
# Response
{
  "creation_date": "2018-10-22T21:55:40.708571+00:00",
  "description": "Build a RESTful API",
  "skills_list": [
    "python",
    "flask",
    "DevOps"
  ],
  "modification_date": "2018-10-22T21:55:40.708578+00:00",
  "id": 1,
  "title": "Backend Engineer"
}
```
- Get all offers for user
```bash
curl -X GET "http://localhost:5000/api/v1/users/1/offers/" -H "accept: application/json" -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJ1c2VyIiwiZXhwaXJlc19hdCI6IjIwMTgtMTAtMjMgMjE6NTM6NDMuODA0MjEyIn0.DIMHTfqqU-SDVW_kLXukh0pc9MOtO7uyvw4oIbXxtL4"
# Response
{
  "offers": [
    {
      "creation_date": "2018-10-22T21:55:40.708571+00:00",
      "description": "Build a RESTful API",
      "skills_list": [
        "python",
        "flask",
        "DevOps"
      ],
      "modification_date": "2018-10-22T21:55:40.708578+00:00",
      "id": 1,
      "title": "Backend Engineer"
    }
  ],
  "count": 1
}
```
- Edit a job offer
```bash
curl -X PUT "http://localhost:5000/api/v1/users/1/offers/1" -H "accept: application/json" -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJ1c2VyIiwiZXhwaXJlc19hdCI6IjIwMTgtMTAtMjMgMjE6NTM6NDMuODA0MjEyIn0.DIMHTfqqU-SDVW_kLXukh0pc9MOtO7uyvw4oIbXxtL4" -H "Content-Type: application/json" -d "{ \"title\": \"DevOps Engineer\"}"
# Response
{
  "creation_date": "2018-10-22T21:55:40.708571+00:00",
  "description": "Build a RESTful API",
  "skills_list": [
    "python",
    "flask",
    "DevOps"
  ],
  "modification_date": "2018-10-22T22:58:31.279914+00:00",
  "id": 1,
  "title": "DevOps Engineer"
}
```
- Get a single offer by id
```bash
curl -X GET "http://localhost:5000/api/v1/users/1/offers/1" -H "accept: application/json" -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJ1c2VyIiwiZXhwaXJlc19hdCI6IjIwMTgtMTAtMjMgMjE6NTM6NDMuODA0MjEyIn0.DIMHTfqqU-SDVW_kLXukh0pc9MOtO7uyvw4oIbXxtL4"
# Response
{
  "creation_date": "2018-10-22T21:55:40.708571+00:00",
  "description": "Build a RESTful API",
  "skills_list": [
    "python",
    "flask",
    "DevOps"
  ],
  "modification_date": "2018-10-22T22:58:31.279914+00:00",
  "id": 1,
  "title": "DevOps Engineer"
}
```
- Delete an offer
```bash
curl -X DELETE "http://localhost:5000/api/v1/users/1/offers/1" -H "accept: application/json" -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJ1c2VyIiwiZXhwaXJlc19hdCI6IjIwMTgtMTAtMjMgMjE6NTM6NDMuODA0MjEyIn0.DIMHTfqqU-SDVW_kLXukh0pc9MOtO7uyvw4oIbXxtL4"
# Response
{
  "message": "offer deleted 1"
}
```

### API Swagger

All API endpoints can be requested from the swagger UI

![](swagger.png)

> **Tip**: Use Authorize button to load your JWT after login.

## CI/CD pipeline

Gitlab CI/CD pipeline is responsible for running jobs after each code push, it includes the following stages:

- Build: Build the application docker image.
- Test: Run integration tests agianst the built image to check the code validity.
- Staging: Deploy the application to staging environment for further testing.
- Production: Deploy the application to production environment

## Deployment

The deployment is done automatically to staging environment after pushing the code, you can check the deploy stage in `.gitlab-ci.yml` to see how the deployment is performed.

The `helm` tool was used to deploy to kubernetes, Helm supports many features such as rolling upgrades and rollbacks with all the changes being version controlled.

The deployments environments for the pipeline are:
- staging: https://job-offers-api-staging.apps.abdelhalimresu.com/
- production: https://job-offers-api.apps.abdelhalimresu.com/

Traefik was used as ingress class for kubernetes to allow access to application within the cluster.

- Traefik dashboard url: https://apps.abdelhalimresu.com/dashboard/

## Monitoring

### System resources usage monitoring

To monitor the resources usage within the cluser, Prometheus and Grafana were used.

- Link: https://grafana.apps.abdelhalimresu.com/
- Credentials: admin:abdelhalim 

Monitoring is done on many levels:

- Node level
- Deployment level
- Pod level

### Error tracking

Sentry was used for errors reporting and tracking.

- Link: https://sentry.apps.abdelhalimresu.com/sentry/job-offers-flask-api/
- Credentials: abdelhalim.resu@gmail.com:abdelhalim 
