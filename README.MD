# Django XRPL test project

## Get Started
Clone the repository:

`git clone https://github.com/geth-network/django-xrpl-test.git && cd django-xrpl-test`


Prepare env files:

`cp .envs/prod/.django.example .envs/prod/.django && cp .envs/prod/.postgres.example .envs/prod/.postgres`

Build and run docker containers:

`docker-compose up --build -d`

Collect Django static files to static root folder and apply Django migration files:

`docker-compose run xrpl-django bash -c "python manage.py collectstatic && python manage.py migrate"`


Run pytest:

`docker-compose run xrpl-django pytest`

## API Schema
API documentation will be available with ReDoc container:

*http://localhost:8081/*
