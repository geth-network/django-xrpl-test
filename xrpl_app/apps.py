from django.apps import AppConfig
from django.db import ProgrammingError


class XrplAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "xrpl_app"
    default_asset = None

    def ready(self):
        from xrpl_app.models import AssetInfo
        try:
            self.default_asset = AssetInfo.get_default_asset()
        except ProgrammingError:
            pass
