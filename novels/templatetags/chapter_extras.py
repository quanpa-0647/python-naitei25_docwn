from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
import math

register = template.Library()


@register.filter
def format_number(value):
    """Format number with thousands separator"""
    if value is None:
        return "—"
    try:
        return f"{int(value):,}".replace(",", ".")
    except (ValueError, TypeError):
        return value


@register.filter
def reading_time(chapter):
    """Calculate estimated reading time based on word count"""
    if not chapter or not chapter.word_count:
        return _("Unknown")

    words_per_minute = 225
    minutes = math.ceil(chapter.word_count / words_per_minute)

    if minutes < 1:
        return _("< 1 min")
    elif minutes == 1:
        return _("1 min")
    elif minutes < 60:
        return _("%(minutes)d mins") % {'minutes': minutes}
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return _("%(hours)d hour(s)") % {'hours': hours}
        else:
            return _("%(hours)dh %(minutes)dm") % {'hours': hours, 'minutes': remaining_minutes}


@register.inclusion_tag('admin/partials/status_badge.html')
def status_badge(chapter):
    """Render status badge component"""
    if not chapter:
        return {'status': 'unknown', 'text': _('Unknown'), 'icon': 'question'}

    if chapter.approved:
        return {
            'status': 'approved',
            'text': _('Approved'),
            'icon': 'check-circle'
        }
    elif chapter.rejected_reason:
        return {
            'status': 'rejected',
            'text': _('Rejected'),
            'icon': 'times-circle'
        }
    else:
        return {
            'status': 'pending',
            'text': _('Pending Review'),
            'icon': 'clock'
        }
