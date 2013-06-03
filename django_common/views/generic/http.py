import json
from django.http import HttpResponse, HttpResponseRedirect

def ajax_condition(request):
    return request.META.get('HTTP_X_REQUESTED_WITH', None) == 'xmlhttprequest'

class ConditionalJSONResponseView(object):
    """
    Conditionally return a JSON response.
    Response context is the JSON response.
    """
    conditions = []

    def dispatch(self, request, *args, **kwargs):
        response = super(ConditionalJSONResponseView, self).dispatch(request, *args, **kwargs)

        # if not ajax request, process normally.
        if not any([condition(request) for condition in conditions]):
            return response

        response_json_data = {}
        if isinstance(response, HttpResponseRedirect):
            response_json_data['response'] = ''
            response_json_data['redirect'] = response['Location']
        else:
            return HttpResponse(json.dumps(response.context), mimetype="application/json")
