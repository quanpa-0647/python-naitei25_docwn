from django import template
from django.utils.translation import gettext as _

register = template.Library()

@register.filter
def status_display(name):
    progress_map = {
        "ONGOING": _("Đang tiến hành"),
        "COMPLETED": _("Hoàn thành"),
        "SUSPEND": _("Tạm dừng"),
    }
    approval_map = {
        "DRAFT": _("Nháp"),
        "PENDING": _("Chờ duyệt"),
        "APPROVED": _("Đã duyệt"),
        "REJECTED": _("Bị từ chối"),
    }
    mapping = {**progress_map, **approval_map}
    return mapping.get(name, name)
