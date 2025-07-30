from social_core.exceptions import AuthForbidden
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

def prevent_duplicate_social_email(backend, details, *args, **kwargs):
    """
    Chặn nếu email đã tồn tại nhưng chưa từng login qua social auth.
    """
    email = details.get('email')

    if not email:
        return

    user = User.objects.filter(email=email).first()
    social = backend.strategy.storage.user.get_social_auth(backend.name, kwargs.get('uid'))

    if user and not social:
        # User có email này tồn tại, nhưng chưa liên kết tài khoản Google
        raise AuthForbidden(backend, _("Email này đã tồn tại nhưng chưa liên kết với Google."))
