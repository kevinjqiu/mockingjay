import httpretty

from .builder import EndpointMockBuilder
from .fixture_loader import Jinja2FixtureLoader


class InvalidEndpointSpecException(Exception):
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
    def __init__(
            self, service_prefix, default_headers=None, fixture_root=None):
        self.service_prefix = service_prefix
        self.default_headers = default_headers
        if fixture_root is not None:
            self.fixture_loader = Jinja2FixtureLoader(fixture_root)
        else:
            self.fixture_loader = None

    def endpoint(self, endpoint):
        method, endpoint = _parse_endpoint(endpoint)
        return EndpointMockBuilder(
            method, self.service_prefix + endpoint,
            self.default_headers, self.fixture_loader)
