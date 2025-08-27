from django import template
from django.utils.translation import gettext_lazy as _
from constants import ApprovalStatus

register = template.Library()

@register.filter(name="status_label")
def status_label(status):
    return {
        ApprovalStatus.DRAFT.value: _("Bản nháp"),
        ApprovalStatus.PENDING.value: _("Chờ duyệt"), 
        ApprovalStatus.APPROVED.value: _("Đã duyệt"),
        ApprovalStatus.REJECTED.value: _("Bị từ chối"),
    }.get(status, "")

@register.filter(name="status_icon")
def status_icon(status):
    return {
        ApprovalStatus.DRAFT.value: "bx-edit",
        ApprovalStatus.PENDING.value: "bx-time",
        ApprovalStatus.APPROVED.value: "bx-check",
        ApprovalStatus.REJECTED.value: "bx-x",
    }.get(status, "bx-question-mark")

@register.filter(name="status_class")
def status_class(status):
    return {
        ApprovalStatus.DRAFT.value: "status-draft",
        ApprovalStatus.PENDING.value: "status-pending",
        ApprovalStatus.APPROVED.value: "status-approved", 
        ApprovalStatus.REJECTED.value: "status-rejected",
    }.get(status, "status-unknown")
    
@register.filter(name="chapter_status_label")
def chapter_status_label(chapter):
    if chapter.approved:
        return _("Đã duyệt")
    elif chapter.rejected_reason:
        return _("Bị từ chối")
    else:
        return _("Chờ duyệt")

@register.filter(name="chapter_status_icon")
def chapter_status_icon(chapter):
    if chapter.approved:
        return "bx-check"
    elif chapter.rejected_reason:
        return "bx-x"
    else:
        return "bx-time"

@register.filter(name="chapter_status_class")
def chapter_status_class(chapter):
    if chapter.approved:
        return "status-approved"
    elif chapter.rejected_reason:
        return "status-rejected"
    else:
        return "status-pending"

@register.filter(name="chapter_status_type")
def chapter_status_type(chapter):
    if chapter.approved:
        return "approved"
    elif chapter.rejected_reason:
        return "rejected"
    else:
        return "pending"
