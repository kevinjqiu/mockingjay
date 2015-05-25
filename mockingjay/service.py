import httpretty
from .builder import EndpointMockBuilder



class InvalidEndpointSpecException(StandardError):
    pass


VALID_METHODS = set([
    'GET', 'PUT', 'POST', 'DELETE', 'HEAD',
    'PATCH', 'OPTIONS', 'CONNECT'])


def _parse_endpoint(spec):
    try:
        method_str, endpoint = spec.strip().split(' ')
    except ValueError:
        raise InvalidEndpointSpecException()
    else:
        method_str = method_str.upper()
        if method_str in VALID_METHODS:
            return getattr(httpretty, method_str), endpoint
        raise InvalidEndpointSpecException()


class MockService(object):
    def __init__(self, service_prefix):
        self.service_prefix = service_prefix

    def endpoint(self, endpoint):
        method, endpoint = _parse_endpoint(endpoint)
        return EndpointMockBuilder(
            method,
            self.service_prefix + endpoint)
