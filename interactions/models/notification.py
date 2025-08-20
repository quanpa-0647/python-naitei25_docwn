from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from accounts.models import User
from constants import (
    MAX_TYPE_LENGTH,
    MAX_TITLE_LENGTH,
    DATE_FORMAT_DMY2,
    NotificationTypeChoices,
)

class Notification(models.Model):
    """Thông báo cho người dùng"""
    user = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        verbose_name=_("Người dùng"),
        related_name='notifications'
    )
    
    type = models.CharField(
        max_length=MAX_TYPE_LENGTH,
        choices=NotificationTypeChoices.CHOICES,
        verbose_name=_("Loại thông báo")
    )
    
    title = models.CharField(
        max_length=MAX_TITLE_LENGTH, 
        verbose_name=_("Tiêu đề")
    )
    
    content = models.TextField(verbose_name=_("Nội dung"))
    
    is_read = models.BooleanField(
        default=False, 
        verbose_name=_("Đã đọc")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_("Ngày tạo")
    )
    
    # Generic relationship - thay thế cho các related_* fields
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Loại đối tượng")
    )
    object_id = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name=_("ID đối tượng")
    )
    related_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _("Thông báo")
        verbose_name_plural = _("Thông báo")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['type', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username if self.user else 'Unknown'}"

    def mark_as_read(self):
        """Đánh dấu thông báo là đã đọc"""
        self.is_read = True
        self.save(update_fields=['is_read'])

    @property
    def related_object_name(self):
        """Lấy tên của đối tượng liên quan"""
        if self.related_object:
            return str(self.related_object)
        return None
