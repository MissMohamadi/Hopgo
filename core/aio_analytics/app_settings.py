from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Google tag setup 
GTAG_TOKEN_ID = getattr(settings, "GTAG_TOKEN_ID", None)

