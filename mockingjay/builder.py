import json
import httpretty


class EndpointMockBuilder(object):
    def __init__(self, method, endpoint, default_headers, fixture_loader):
        self.method, self.endpoint = method, endpoint
        self.return_code = 200
        self.return_headers = default_headers or {}
        self.return_body = None
        self.fixture_loader = fixture_loader

    def should_return(self, code, headers, body):
        self.return_code = code
        self.return_headers = headers
        self.return_body = body
        return self

    def should_return_code(self, code):
        self.return_code = code
        return self

    def should_return_header(self, key, value):
        self.return_headers[key.lower()] = value
        return self

    def should_return_body(self, body):
        self.return_body = body
        return self

    def should_return_body_from_fixture(self, template_file, **params):
        assert self.fixture_loader is not None, "fixture_loader not set"
        self.return_body = self.fixture_loader.render(template_file, **params)
        return self

    def should_return_json(self, json_object):
        self.return_body = json.dumps(json_object)
        return self

    def register(self):
        httpretty.register_uri(
            self.method, self.endpoint, body=self.return_body,
            adding_headers=self.return_headers, status=self.return_code)
