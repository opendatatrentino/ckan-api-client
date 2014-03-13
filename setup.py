import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

version = '0.1-alpha'

install_requires = [
    "requests",
]

if sys.version_info < (2, 7):
    install_requires.append('ordereddict')

tests_require = [
    'pytest',
    'psycopg2',
    'solrpy',
]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--ignore=build',
            '--verbose',
            # '--cov=...',
            # '--cov-report=term-missing',
            '--pep8',
            'datacat']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='ckan-api-client',
    version=version,
    packages=find_packages(),
    url='http://rshk.github.io/ckan-api-client',
    license='BSD License',
    author='Samuele Santi',
    author_email='s.santi@trentorise.eu',
    description='',
    long_description='',
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='ckan_api_client.tests',
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 2.7",
    ],
    package_data={'': ['README.md', 'LICENSE']},
    cmdclass={'test': PyTest})
