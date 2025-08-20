from django import template

register = template.Library()

@register.simple_tag
def pagination_range(page_obj, num_pages_to_show=1):
    current = page_obj.number
    last = page_obj.paginator.num_pages
    start = max(current - num_pages_to_show, 1)
    end = min(current + num_pages_to_show, last)

    pages = []
    if start > 1:
        pages.append(1)
        if start > 2:
            pages.append("...")

    for i in range(start, end + 1):
        pages.append(i)

    if end < last:
        if end < last - 1:
            pages.append("...")
        pages.append(last)

    return pages
