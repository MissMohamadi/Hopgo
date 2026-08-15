from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# module general configs
OFFLINE_CAPTCHA_ADMIN_ENABLE = getattr(
    settings, "OFFLINE_CAPTCHA_ADMIN_ENABLE", False
)
