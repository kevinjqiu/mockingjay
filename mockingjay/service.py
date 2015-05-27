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
        method_str, endpoint = str(spec).strip().split(' ')
    except ValueError:
        raise InvalidEndpointSpecException()
    else:
        method_str = method_str.upper()
        if method_str in VALID_METHODS:
            return getattr(httpretty, method_str), endpoint
        raise InvalidEndpointSpecException()


def _get_host_from_raw_request(raw_request):
    for line in raw_request.splitlines():
        try:
            key, value = str(line).split(':', 1)
        except ValueError:
            pass
        else:
            if key == 'Host':
                return value.strip()
    return None


def _get_scheme_from_protocol_version(protocol_version):
    return str(protocol_version).split('/')[0].lower()


def _get_service_prefix_from_request(request):
    return "%s://%s" % (
        _get_scheme_from_protocol_version(request.protocol_version),
        _get_host_from_raw_request(request.raw_headers))


class MockService(object):
    def __init__(
            self, service_prefix, default_headers=None, fixture_root=None):
        self.service_prefix = service_prefix
        self.default_headers = default_headers
        if fixture_root is not None:
            self.fixture_loader = Jinja2FixtureLoader(fixture_root)
        else:
            self.fixture_loader = None

        self.endpoints = []

    def endpoint(self, endpoint):
        """
        Create an EndpointMockBuilder object based on the given endpoint
        """
        method, endpoint = _parse_endpoint(endpoint)
        retval = EndpointMockBuilder(
            method, self.service_prefix + endpoint,
            self.default_headers, self.fixture_loader)
        self.endpoints.append(retval)
        return retval

    def clear_mocks(self):
        """
        Clear the endpoint mocks that have been registered for the service
        """
        self.endpoints.clear()

    def assert_requests_matched(self):
        requests = [
            request for request in httpretty.httpretty.latest_requests
            if _get_service_prefix_from_request(request) == self.service_prefix
        ]
        for endpoint in self.endpoints:
            requests = [
                request for request in requests
                if "%s%s" % (
                    _get_service_prefix_from_request(request),
                    request.path) == endpoint.endpoint
                and request.method == endpoint.method
            ]

            for request in requests:
                endpoint.matches(request)
