from django import template
from django.utils import timezone
from django.utils.formats import date_format

register = template.Library()


@register.filter
def localtime_format(value, format_string=None):
    """
    Convert datetime to local timezone and format it
    Usage: {{ datetime_value|localtime_format:"d/m/Y H:i" }}
    """
    if not value:
        return ''
    
    # Convert to local timezone
    local_dt = timezone.localtime(value)
    
    # Format the datetime
    if format_string:
        return date_format(local_dt, format_string)
    else:
        return date_format(local_dt)


@register.filter
def to_localtime(value):
    """
    Convert datetime to local timezone
    Usage: {{ datetime_value|to_localtime|date:"d/m/Y H:i" }}
    """
    if not value:
        return value
    return timezone.localtime(value)
