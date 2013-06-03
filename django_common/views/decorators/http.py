import logging, json
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.
from django.utils.decorators import available_attrs
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse

logger = logging.getLogger(__name__)

def json_response(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        response_json_data = {}
        if isinstance(response, TemplateResponse):
            response_json_data['response'] = response.render().rendered_content
            response_json_data['redirect'] = ''
        elif isinstance(response, HttpResponseRedirect):
            response_json_data['response'] = ''
            response_json_data['redirect'] = response['Location']
        else:
            response_json_data['response'] = response.content
            response_json_data['redirect'] = ''
        return HttpResponse(json.dumps(response_json_data), mimetype="application/json")
    return _wrapped_view