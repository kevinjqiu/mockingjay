"""
test_mockingjay
----------------------------------

Tests for `mockingjay` module.
"""

import requests
import httpretty
import pytest
import os.path

from mockingjay.service import (
    MockService, _parse_endpoint, InvalidEndpointSpecException)


def test_parse_endpoint_valid_format():
    def assert_valid_format(spec, method, endpoint):
        method, endpt = _parse_endpoint(spec)
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
            _parse_endpoint(spec)

    yield assert_invalid_format, "get /v1/ users"
    yield assert_invalid_format, "GOT /v1/users"


class TestMockingjay(object):

    @httpretty.activate
    def test_post_without_header_match(self):
        service = MockService('http://localhost:1234')
        service.endpoint('POST /user') \
            .should_return(200, {}, '{}') \
            .register()
        response = requests.post('http://localhost:1234/user')
        assert response.text == u'{}'

    @httpretty.activate
    def test_get_return_using_build(self):
        service = MockService('http://localhost:1234')
        service.endpoint('GET /me') \
            .should_return_header('Content-Type', 'application/json') \
            .should_return_code(200) \
            .should_return_body('{"me": "ok"}') \
            .register()

        response = requests.get('http://localhost:1234/me')
        assert response.json() == {'me': 'ok'}
        assert response.headers['content-type'] == 'application/json'

    @httpretty.activate
    def test_get_return_using_build_with_default_headers(self):
        service = MockService('http://localhost:1234',
                              {'content-type': 'application/vnd+jsonapi'})
        service.endpoint('GET /me') \
            .should_return_code(200) \
            .should_return_body('{"me": "ok"}') \
            .register()

        response = requests.get('http://localhost:1234/me')
        assert response.json() == {'me': 'ok'}
        assert response.headers['content-type'] == 'application/vnd+jsonapi'

    @httpretty.activate
    def test_get_return_using_build_with_default_header_is_overriden(self):
        service = MockService('http://localhost:1234',
                              {'content-type': 'application/vnd+jsonapi'})
        service.endpoint('GET /me') \
            .should_return_header('content-type', 'application/json') \
            .should_return_code(200) \
            .should_return_body('{"me": "ok"}') \
            .register()

        response = requests.get('http://localhost:1234/me')
        assert response.json() == {'me': 'ok'}
        assert response.headers['content-type'] == 'application/json'

    @httpretty.activate
    def test_get_return_using_fixture_template(self):
        service = MockService('http://localhost:1234',
                              fixture_root=os.path.join(
                                  os.path.dirname(__file__),
                                  'fixtures'))
        service.endpoint('GET /user/1') \
            .should_return_body_from_fixture(
                'user.jinja', customer_id=1, email='foo@example.com') \
            .should_return_header('content_type', 'application/json') \
            .register()
        response = requests.get('http://localhost:1234/user/1')
        assert response.json() == {
            'object': 'customer',
            'created': 1432484442,
            'id': '1',
            'description': 'customer',
            'email': 'foo@example.com',
            'delinquent': False,
        }
