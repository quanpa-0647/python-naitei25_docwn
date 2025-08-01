from django.utils.decorators import method_decorator
from .decorators import (
    require_login,
    require_role,
    require_group,
    require_permission,
    require_owner_or_admin
)

class RequireLoginMixin:
    @method_decorator(require_login)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class RequireRoleMixin:
    allowed_roles = []

    @method_decorator(lambda func: require_role(*RequireRoleMixin.allowed_roles)(func))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return require_role(*cls.allowed_roles)(view)

class RequireGroupMixin:
    group_names = []

    @method_decorator(lambda func: require_group(*RequireGroupMixin.group_names)(func))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return require_group(*cls.group_names)(view)

class RequirePermissionMixin:
    permission_codenames = []

    @method_decorator(lambda func: require_permission(*RequirePermissionMixin.permission_codenames)(func))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return require_permission(*cls.permission_codenames)(view)
    
class RequireOwnerOrAdminMixin:
    def dispatch(self, request, *args, **kwargs):
        @require_owner_or_admin(lambda req, *a, **kw: self.get_object())
        def wrapped_view(req, *a, **kw):
            return super().dispatch(req, *a, **kw)
        return wrapped_view(request, *args, **kwargs)
