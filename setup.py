import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

version = '0.1-alpha'

install_requires = [
    "requests",  # For performing HTTP requests
    "cliff",  # For the CLI
]

if sys.version_info < (2, 7):
    install_requires.append('ordereddict')

tests_require = [
    'pytest',
    'pytest-cov',
    'pytest-pep8',

    ## The next two are required in order to install
    ## Ckan in a separate environment.
    'psycopg2',
    'solrpy',
]

## Shorten names
_cch = 'ckan_api_client.commands.client_hilev'
_ccs = 'ckan_api_client.commands.syncing'

entry_points = {
    'console_scripts': [
        'ckanclient = ckan_api_client.cli:main',
    ],
    'ckan_api_client.cli': [
        'list_datasets = {0}:ListDatasets'.format(_cch),
        'iter_datasets = {0}:IterDatasets'.format(_cch),
        'get_dataset = {0}:GetDataset'.format(_cch),
        'import_dataset = {0}:ImportDataset'.format(_cch),
        'import_directory = {0}:ImportDirectory'.format(_ccs),
        'import_sqlite = {0}:ImportSQLite'.format(_ccs),
    ],
}


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--ignore=build',
            '--verbose',
            # '--cov=ckan_api_client',
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
    cmdclass={'test': PyTest},
    entry_points=entry_points)
