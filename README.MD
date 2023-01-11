# Django XRPL test project

## Get Started
Clone the repository:

`git clone https://github.com/geth-network/django-xrpl-test.git`


Prepare env files:
1) `cp .envs/prod/.django.example .envs/prod/.django` 
2) `cp .envs/prod/.postgres.example .envs/prod/.postgres`

Build and run docker containers:

`docker-compose up --build -d`

Collect Django static files to static root folder:

`docker-compose run xrpl-django manage.py collectstatic`

Apply Django migration files:

`docker-compose run xrpl-django manage.py migrate`



## API Schema
API documentation is available with ReDoc container:

*http://localhost:8081/*
