from django import template
from django.conf import settings
from aio_analytics.app_settings import GTAG_TOKEN_ID
register = template.Library()


@register.inclusion_tag('analytics/google-tag.html')
def add_google_tag():
    if settings.DEBUG:
        return None
    else:
        return {'google_tag_id': GTAG_TOKEN_ID}
