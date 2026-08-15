from django import template
from django.contrib.auth import get_user_model
import jdatetime
from django.conf import settings


User = get_user_model()

register = template.Library()


import pytz
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

