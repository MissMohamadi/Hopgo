from django import template
from django.contrib.auth import get_user_model
from django.core.cache import cache
import jdatetime
from django.conf import settings

from django.utils.timezone import now
from django.db.models import Sum

User = get_user_model()

register = template.Library()


@register.simple_tag(takes_context=True)
def get_user_type(context):
    request = context['request']
    user = request.user
    return user.get_type_display()


@register.simple_tag()
def count_users():
    return User.objects.filter(is_superuser=False).count()

@register.simple_tag()
def count_newsletters():
    return NewsLetter.objects.all().count()


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


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def sum(value, arg):
    return value + arg