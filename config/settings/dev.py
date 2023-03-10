from .base import *  # noqa

# https://docs.djangoproject.com/en/4.1/ref/settings/#debug
DEBUG = env.bool("DEBUG", True)  # noqa: F405

# https://docs.djangoproject.com/en/4.1/ref/settings/#secret-key
SECRET_KEY = env(  # noqa: F405
    "DJANGO_SECRET_KEY",
    default="django-insecure-%c-o1mz0w*ne9bd9$hs^0392#p!*rog4ss4(1=^*nd2&n%p$",
)
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
