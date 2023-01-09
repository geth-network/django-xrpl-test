from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY")
SIMPLE_JWT["SIGNING_KEY"] = SECRET_KEY
SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(minutes=5)
SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(days=1)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

# DATABASES
# ------------------------------------------------------------------------------
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)  # noqa F405
