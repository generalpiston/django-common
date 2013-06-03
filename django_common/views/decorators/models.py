import logging, json
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.
from django.db import models
from django.utils.decorators import available_attrs
from django.http import Http404

logger = logging.getLogger(__name__)

def get_object_or_404(id_key, model):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            key = model._meta.concrete_model._meta.object_name.lower()
            if key in kwargs:
                return view_func(request, *args, **kwargs)
            if id_key in kwargs:
                try:
                    kwargs[key] = model.objects.get(pk=kwargs[id_key])
                except Exception as e:
                    logger.warn(e)
                    raise Http404
                return view_func(request, *args, **kwargs)
            raise Http404
        return _wrapped_view
    return decorator
