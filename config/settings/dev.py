from datetime import timedelta

from .base import *  # noqa

# https://docs.djangoproject.com/en/4.1/ref/settings/#debug
DEBUG = env.bool("DEBUG", True)

# https://docs.djangoproject.com/en/4.1/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-%c-o1mz0w*ne9bd9$hs^0392#p!*rog4sseo4(1=^*nd2&n%p$",
)
SIMPLE_JWT["SIGNING_KEY"] = SECRET_KEY
SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(hours=4)
SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(days=1)
# https://docs.djangoproject.com/en/4.1/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ["debug_toolbar"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
if env("USE_DOCKER") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]
