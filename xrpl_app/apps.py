from django.apps import AppConfig
from django.db import ProgrammingError


class XrplAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "xrpl_app"
