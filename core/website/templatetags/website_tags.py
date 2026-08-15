import pytz
from django import template
from django.utils.html import strip_spaces_between_tags, strip_tags
from django.utils.text import Truncator
from django.utils import timezone
from django.db.models import F

from django.core.cache import cache
from django.contrib.auth import get_user_model
import jdatetime
from django.conf import settings

register = template.Library()

User = get_user_model()


@register.filter(name='excerpt')
def excerpt_with_ptag_spacing(value, arg):
    try:
        limit = int(arg)
    except ValueError:
        return 'Invalid literal for int().'

    # remove spaces between tags
    value = strip_spaces_between_tags(value)

    # add space before each P end tag (</p>)
    value = value.replace("</p>", " </p>")
    value = value.replace("&quot", "  ")
    # strip HTML tags
    value = strip_tags(value)

    # other usage: return Truncator(value).words(length, html=True, truncate=' see more')
    return Truncator(value).words(limit)



@register.simple_tag
def user_count():
    count = cache.get('user_count')
    if count is None:
        count = User.objects.count()
        cache.set('user_count', count, 60 * 60)  # cache for 5 minutes
    return count


@register.filter(name='jalali_time')
def jalali_time(value, format_str="%Y/%m/%d %H:%M:%S"):
    # Convert the input datetime object to the UTC time zone
    utc_time = value.astimezone(pytz.utc)
    # Convert the UTC time to the local time zone
    local_time = utc_time.astimezone(pytz.timezone(settings.TIME_ZONE))
    # Convert the local time to a Jalali datetime object
    jdatetime.set_locale('fa_IR')
    jtime = jdatetime.datetime.fromgregorian(datetime=local_time)
    # Convert the Jalali datetime object to a formatted string
    return jtime.strftime(format_str)
