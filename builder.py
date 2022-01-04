from setuptools import Extension
from setuptools.command.build_ext import build_ext


class DummyExtension(Extension):
    def __init__(self, name):
        Extension.__init__(self, name, sources=[])


class DummyBuild(build_ext):
    def build_extension(self, ext):
        pass
