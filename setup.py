#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import sys
import tomllib
from pathlib import Path
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
    pyproject = Path(__file__).parent / "pyproject.toml"
    with pyproject.open("rb") as f:
        return tomllib.load(f)["project"]["version"]

    # import gocd_cli
    # return gocd_cli.__version__

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='gocd-cli',
    author='Björn Andersson',
    author_email='ba@sanitarium.se',
    license='MIT License',
    url='https://github.com/gaqzi/gocd-cli/',
    description='A CLI client for interacting with Go Continuous Delivery',
    long_description=README,
    version=version(),
    packages=find_packages(exclude=('tests',)),
    namespace_packages=('gocd_cli', 'gocd_cli.commands', 'gocd_cli.encryption'),
    cmdclass={'test': PyTest},
    scripts=('bin/gocd',),
    install_requires=[
        'gocd>=1.0.0',
    ],
    tests_require=[
        'pytest',
        'mock==1.0.1'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.12.12'
    ],
    python_requires='==3.12.12'
)
