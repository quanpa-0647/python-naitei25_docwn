from django import template

register = template.Library()

@register.filter
def message_icon(tag):
    icons = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle', 
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle',
        'debug': 'fas fa-bug'
    }
    return icons.get(tag, 'fas fa-info-circle')

@register.inclusion_tag('admin/partials/_messages.html')
def show_messages(messages, dismissible=False, show_icons=True):
    return {
        'messages': messages,
        'dismissible': dismissible,
        'show_icons': show_icons
    }
