import httpretty


class EndpointMockBuilder(object):
    def __init__(self, method, endpoint):
        self.method, self.endpoint = method, endpoint
        self.return_code = None
        self.return_headers = None
        self.return_body = None

    def should_return(self, code, headers, body):
        self.return_code = code
        self.return_headers = headers
        self.return_body = body
        return self

    def register(self):
        httpretty.register_uri(
            self.method, self.endpoint, body=self.return_body)
