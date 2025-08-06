from django import template
from django.core.paginator import Page
from constants import (
    PAGINATION_PAGE_RANGE, 
    PAGINATION_TEMPLATE_PATH,
    PAGINATION_MIN_PAGE,
    PAGINATION_ELLIPSIS_THRESHOLD,
    PAGINATION_MIN_PAGES_TO_SHOW
)

register = template.Library()

@register.inclusion_tag(PAGINATION_TEMPLATE_PATH, takes_context=True)
def pagination_with_range(context, page_obj, page_range=PAGINATION_PAGE_RANGE):
    """
    Template tag to render pagination with a configurable page range.
    
    Usage:
    {% load admin_pagination_tags %}
    {% pagination_with_range page_obj %}
    """
    
    if not hasattr(page_obj, 'number'):
        return {'show_pagination': False}
    
    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages
    
    # Calculate start and end page numbers
    start_page = max(PAGINATION_MIN_PAGE, current_page - page_range)
    end_page = min(total_pages, current_page + page_range)
    
    # Adjust start_page if we're near the end
    if end_page - start_page < PAGINATION_ELLIPSIS_THRESHOLD * page_range:
        start_page = max(PAGINATION_MIN_PAGE, end_page - PAGINATION_ELLIPSIS_THRESHOLD * page_range)
    
    # Adjust end_page if we're near the beginning  
    if end_page - start_page < PAGINATION_ELLIPSIS_THRESHOLD * page_range:
        end_page = min(total_pages, start_page + PAGINATION_ELLIPSIS_THRESHOLD * page_range)
    
    page_numbers = list(range(start_page, end_page + PAGINATION_MIN_PAGE))
    
    # Add ellipsis logic
    show_first_ellipsis = start_page > PAGINATION_ELLIPSIS_THRESHOLD
    show_last_ellipsis = end_page < total_pages - PAGINATION_MIN_PAGE
    show_first_page = start_page > PAGINATION_MIN_PAGE
    show_last_page = end_page < total_pages
    
    template_context = {
        'page_obj': page_obj,
        'page_numbers': page_numbers,
        'show_first_page': show_first_page,
        'show_last_page': show_last_page,
        'show_first_ellipsis': show_first_ellipsis,
        'show_last_ellipsis': show_last_ellipsis,
        'show_pagination': total_pages > PAGINATION_MIN_PAGES_TO_SHOW,
        'request': context.get('request'),  # Pass request from context
    }
    
    return template_context

@register.simple_tag
def url_replace(request, field, value):
    """
    Replace a GET parameter in the current URL.
    
    Usage:
    {% url_replace request 'page' 2 %}
    """
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()
