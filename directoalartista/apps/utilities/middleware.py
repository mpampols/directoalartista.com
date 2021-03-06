from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.utils.decorators import decorator_from_middleware

CONTENT_TYPES = ('text/html','application/xhtml+xml','application/xml')
HEADER_VALUE = getattr(settings, 'X_UA_COMPATIBLE', 'IE=edge,chrome=1')

class XUACompatibleMiddleware(object):

    def __init__(self, value=None):

        self.value = value
        if value is None:
            self.value = HEADER_VALUE
        if not self.value:
            raise MiddlewareNotUsed

    def process_response(self, request, response):
        response_ct = response.get('Content-Type','').split(';', 1)[0].lower()
        if response_ct in CONTENT_TYPES:
            if not 'X-UA-Compatible' in response:
                response['X-UA-Compatible'] = self.value
        return response

xuacompatible = decorator_from_middleware(XUACompatibleMiddleware)