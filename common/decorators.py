from functools import wraps
from django.shortcuts import get_object_or_404

def require_active_novel(view_func):
    @wraps(view_func)
    def wrapper(request, novel_slug, *args, **kwargs):
        from novels.models import Novel
        
        novel = get_object_or_404(Novel, slug=novel_slug, deleted_at__isnull=True)
        request.novel = novel
        return view_func(request, novel_slug, *args, **kwargs)
    return wrapper
