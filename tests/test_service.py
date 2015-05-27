"""
test_mockingjay
----------------------------------

Tests for `mockingjay` module.
"""

import re
import requests
import httpretty
import pytest
import os.path

from mockingjay.service import (
    MockService, _parse_endpoint, _get_host_from_raw_request,
    InvalidEndpointSpecException)


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


def test_get_host_from_raw_request():
    raw_request = (
        "POST /user HTTP/1.1\r\n"
        "Host: localhost:1234\r\n"
        "Accpet: application/json\r\n"
        "Content-Length: 0\r\n"
        "Accept-Encoding: gzip, deflate, compress\r\n"
        "Accept: */*\r\n"
        "User-Agent: python-requests/2.2.1 CPython/2.7.3 Linux/2.6.18-308.el5"
    )

    assert 'localhost:1234' == _get_host_from_raw_request(raw_request)


class TestResponseBuilder(object):

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

    @httpretty.activate
    def test_get_return_alternate_return_status(self):
        service = MockService('http://localhost:1234')
        service.endpoint('GET /user/1') \
            .should_return_code(404) \
            .should_return_body('{}') \
            .register()
        response = requests.get('http://localhost:1234/user/1')
        assert response.status_code == 404

    @httpretty.activate
    def test_get_return_mock_response_using_object(self):
        service = MockService('http://localhost:1234')
        service.endpoint('GET /user/1') \
            .should_return_code(404) \
            .should_return_json({'error': 'not found'}) \
            .register()
        response = requests.get('http://localhost:1234/user/1')
        assert response.status_code == 404
        assert response.json() == {'error': 'not found'}


class TestRequestMatcher(object):
    def setup(self):
        self.service = MockService('http://localhost:1234')

    def request_match_setup(self, builder_method, builder_args, req_kwargs):
        endpt = self.service.endpoint('POST /user')
        getattr(endpt, builder_method)(*builder_args) \
            .should_return(200, {}, '{}') \
            .register()
        requests.post('http://localhost:1234/user', **req_kwargs)

    def assert_request_match(self, builder_method, builder_args, req_kwargs):
        self.request_match_setup(builder_method, builder_args, req_kwargs)
        self.service.assert_requests_matched()

    def assert_request_not_match(
            self, builder_method, builder_args, req_kwargs):
        self.request_match_setup(builder_method, builder_args, req_kwargs)
        with pytest.raises(AssertionError):
            self.service.assert_requests_matched()

    @httpretty.activate
    def test_request_header_match(self):
        self.assert_request_match(
            'expect_request_header',
            ('X-CorrelationId', 'abcd'),
            {"headers": {'X-CorrelationId': 'abcd'}})

    @httpretty.activate
    def test_request_header_pattern_match(self):
        self.assert_request_match(
            'expect_request_header',
            ('X-CorrelationId', re.compile('ab.d')),
            {"headers": {'X-CorrelationId': 'abcd'}})

    @httpretty.activate
    def test_request_header_not_match(self):
        self.assert_request_not_match(
            'expect_request_header',
            ('X-CorrelationId', 'abcd'),
            {"headers": {'X-CorrelationId': 'beef'}})

    @httpretty.activate
    def test_request_header_pattern_not_match(self):
        self.assert_request_not_match(
            'expect_request_header',
            ('X-CorrelationId', 'ab.d'),
            {"headers": {'X-CorrelationId': 'abd'}})

    @httpretty.activate
    def test_request_body_match(self):
        self.assert_request_match(
            'expect_request_body',
            ('foo=bar',),
            {"data": "foo=bar"})

    @httpretty.activate
    def test_request_body_match_pattern(self):
        self.assert_request_match(
            'expect_request_body',
            (re.compile('foo=(\w+)'),),
            {"data": "foo=quux"})

    @httpretty.activate
    def test_request_body_not_match(self):
        self.assert_request_not_match(
            'expect_request_body',
            ('foo=1',),
            {"data": "foo=quux"})

    @httpretty.activate
    def test_request_body_pattern_not_match(self):
        self.assert_request_not_match(
            'expect_request_body',
            ('foo=(\w+)',),
            {"data": "foo=5"})

    @httpretty.activate
    def test_request_user_match(self):
        self.assert_request_match(
            'expect_request_user',
            ('admin', 'admin',),
            {'auth': ('admin', 'admin')})

    @httpretty.activate
    def test_request_user_nopwd_match(self):
        self.assert_request_match(
            'expect_request_user',
            ('admin',),
            {'auth': ('admin', '')})

    @httpretty.activate
    def test_request_user_not_match(self):
        self.assert_request_not_match(
            'expect_request_user',
            ('admin:pwd',),
            {'auth': ('admin', 'admin')})

    @httpretty.activate
    def test_request_content_type_match(self):
        self.assert_request_match(
            'expect_request_content_type',
            ('application/x-pdf',),
            {'headers': {'content-type': 'application/x-pdf'}})

    @httpretty.activate
    def test_request_content_type_not_match(self):
        self.assert_request_not_match(
            'expect_request_content_type',
            ('application/json',),
            {'headers': {'content-type': 'application/x-pdf'}})
