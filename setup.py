#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def version():
    import gocd
    return gocd.__version__


setup(
    name='gocd_cli',
    author='Björn Andersson',
    author_email='ba@sanitarium.se',
    license='MIT License',
    version=version(),
    packages=find_packages(exclude=('tests',)),
    namespace_packages=('gocd_cli', 'gocd_cli.commands',),
    cmdclass={'test': PyTest},
    requires=[
        'gocd_cli',
    ],
    tests_require=[
        'pytest',
    ],
)
