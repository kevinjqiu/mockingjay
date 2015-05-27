import abc
import re


class StringOrPattern(object):
    """
    A decorator object that wraps a string or a regex pattern so that it can
    be compared against another string either literally or using the pattern.
    """
    def __init__(self, subject):
        self.subject = subject

    def __eq__(self, other_str):
        if isinstance(self.subject, re._pattern_type):
            return self.subject.search(other_str) is not None
        else:
            return self.subject == other_str

    def __hash__(self):
        return self.subject.__hash__()


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
        self.value = StringOrPattern(value)

    def assert_request_matched(self, request):
        assert request.headers.get(self.key) == self.value


class BodyMatcher(Matcher):
    """
    Matcher for the request body.

    :param body: can either be a string or a :class:`_sre.SRE_Pattern`: object
    """

    def __init__(self, body):
        self.body = StringOrPattern(body)

    def assert_request_matched(self, request):
        assert request.body == self.body
