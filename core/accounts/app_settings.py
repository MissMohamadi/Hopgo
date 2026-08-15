from django.conf import settings


# Custom User Management
LOGIN_REDIRECT_URL = getattr(settings, "LOGIN_REDIRECT_URL", "/")
