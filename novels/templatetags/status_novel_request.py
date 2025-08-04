from django import template
from django.utils.translation import gettext as _
from constants import ApprovalStatus

register = template.Library()

STATUS_LABELS = {
    ApprovalStatus.DRAFT.value: _("Bản nháp"),
    ApprovalStatus.PENDING.value: _("Đang chờ duyệt"), 
    ApprovalStatus.APPROVED.value: _("Đã duyệt"),
    ApprovalStatus.REJECTED.value: _("Bị từ chối"),
}

STATUS_CLASSES = {
    ApprovalStatus.DRAFT.value: "bg-secondary",
    ApprovalStatus.PENDING.value: "bg-warning text-dark",
    ApprovalStatus.APPROVED.value: "bg-success",
    ApprovalStatus.REJECTED.value: "bg-danger",
}

@register.filter
def approval_label(status_code):
    return STATUS_LABELS.get(status_code, _("Không xác định"))

@register.filter
def approval_class(status_code):
    return STATUS_CLASSES.get(status_code, "bg-secondary")
