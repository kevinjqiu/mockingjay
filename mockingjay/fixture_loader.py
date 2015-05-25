import abc
from jinja2 import Environment, FileSystemLoader


class FixtureLoader(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def render(fixture_file, **params):
        """
        Return the rendered fixture file according to the params.
        """


class Jinja2FixtureLoader(FixtureLoader):
    def __init__(self, fixture_root):
        self.fixture_root = fixture_root
        self.jinja_env = Environment(loader=FileSystemLoader(fixture_root))

    def render(self, fixture_file, **params):
        return self.jinja_env.get_template(fixture_file).render(**params)
