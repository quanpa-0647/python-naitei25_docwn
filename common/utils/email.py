from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _


def send_password_reset_email(to_email, subject, message):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )
