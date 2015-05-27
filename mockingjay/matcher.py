import abc
import re


class Matcher(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def assert_request_matched(self, request):
        """
        Assert that the request matched the spec in this matcher object.
        """


class HeaderMatcher(Matcher):
    """
    Matcher for the request's header.

    :param key: the name of the header
    :param value: the value of the header
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def assert_request_matched(self, request):
        assert request.headers.get(self.key) == self.value


class BodyMatcher(Matcher):
    """
    Matcher for the request body.

    :param body: can either be a string or a :class:`_sre.SRE_Pattern`: object
    """

    def __init__(self, body):
        self.body = body

    def assert_request_matched(self, request):
        if isinstance(self.body, re._pattern_type):
            assert self.body.search(request.body) is not None
        else:
            assert request.body == self.body
