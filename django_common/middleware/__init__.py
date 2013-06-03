from django.http import HttpResponseRedirect
from django.conf import settings

class SetRemoteAddrMiddleware(object):
    def process_request(self, request):
        if not request.META.has_key('REMOTE_ADDR'):
            try:
                request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
            except:
                request.META['REMOTE_ADDR'] = '1.1.1.1'

class SetUserAgentMiddleware(object):
    def process_request(self, request):
        if not request.META.has_key('HTTP_USER_AGENT'):
            try:
                request.META['HTTP_USER_AGENT'] = request.META['REMOTE_ADDR']
            except:
                request.META['HTTP_USER_AGENT'] = '1.1.1.1'

class BetaOrSplash(object):
    def __allowed_path(self, request):
        for path in getattr(settings, 'BOS_ALLOWED_PATHS', []):
            if request.path.startswith(path):
                return True
        return False

    def process_request(self, request):
        if request.META['REMOTE_ADDR'] in getattr(settings, 'BOS_ALLOWED_IP', []):
            pass
        elif getattr(settings, 'BOS_ALLOWED_QUERY_PARAM', None) in request.GET:
            pass
        elif request.path == getattr(settings, 'BOS_SPLASH_URI', '/underconstruction/'):
            pass
        elif self.__allowed_path(request):
            pass
        else:
            return HttpResponseRedirect(settings.BOS_SPLASH_URI)