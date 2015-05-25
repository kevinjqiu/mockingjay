"""
test_mockingjay
----------------------------------

Tests for `mockingjay` module.
"""

import requests
import httpretty
import pytest

from mockingjay.service import (
    MockService, _parse_endpoint, InvalidEndpointSpecException)


def test_parse_endpoint_valid_format():
    def assert_valid_format(spec, method, endpoint):
        method, endpt = _parse_endpoint("get /v1/users")
        assert method == method
        assert endpt == endpoint

    yield assert_valid_format, "get /v1/users", httpretty.GET, '/v1/users'
    yield assert_valid_format, "GET /v1/users", httpretty.GET, '/v1/users'
    yield assert_valid_format, " Get /v1/users ", httpretty.GET, '/v1/users'
    yield assert_valid_format, "head /v1/users", httpretty.HEAD, '/v1/users'
    yield assert_valid_format, "options /v1/users", \
        httpretty.OPTIONS, '/v1/users'


def test_parse_endpoint_invalid_format():
    def assert_invalid_format(spec):
        with pytest.raises(InvalidEndpointSpecException):
            _parse_endpoint("get /v1/ users")

    yield assert_invalid_format, "get /v1/ users"
    yield assert_invalid_format, "GOT /v1/users"
    yield assert_invalid_format, "GET /v1/users "
    yield assert_invalid_format, "GET /v1/users "


class TestMockingjay(object):

    @httpretty.activate
    def test_post_without_header_match(self):
        service = MockService('http://localhost:1234')
        service.endpoint('POST /user') \
            .should_return(200, {}, '{}') \
            .register()
        response = requests.post('http://localhost:1234/user')
        assert response.text == u'{}'
