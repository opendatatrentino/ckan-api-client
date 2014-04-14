# Ckan API client

Improved Python client for the [Ckan](http://ckan.org) API.

[![Build Status](https://travis-ci.org/opendatatrentino/ckan-api-client.png?branch=master)](https://travis-ci.org/opendatatrentino/ckan-api-client) Master branch

[![Build Status](https://travis-ci.org/opendatatrentino/ckan-api-client.png?branch=develop)](https://travis-ci.org/opendatatrentino/ckan-api-client) Development branch

This package provides:

- a **low-level client**, which is pretty much just a wrapper around
  HTTP calls, handling serialization and exception-raising.

- a **high-level client**, attempting to make it easier / safer to perform
  certain operations on a ckan catalog.

- a **synchronization client**, used to provide some automation
  for synchronization tasks of collections of datasets into a catalog
  (commonly referred to as "harvesting").


Other than that, it attempts to get work around some common issues
with that API, such as inconsistencies and bugs, trying to make
sure problems are discovered earlier.


## Documentation

Documentation is hosted on GitHub pages here: https://opendatatrentino.github.io/ckan-api-client/


## Running tests (new way)

We use gnu make to better automate things:

```
make -f scripts/tests.mk run-tests
```

or

```
make -f scripts/tests.mk run-tests \
CKAN_POSTGRES_ADMIN=postgresql://localhost/postgres \
CKAN_SOLR=http://127.0.0.1:8983/solr \
CKAN_ENV_NAME=ckan-master \
REPO_URL=https://github.com/ckan/ckan \
REPO_BRANCH=master \
PYTHON=/usr/bin/python2.7
```

This will automatically create a suitable environment in ``./ckan-envs/``,
install the selected Ckan branch and run tests using that instance.


## Running tests (old way)

You'll need:

- Python virtualenv, with Ckan installed
- PostgreSQL instance, with administrative access
- Solr instance, with Ckan schema installed


To configure & run tests:

```bash
export CKAN_VIRTUALENV=$VIRTUAL_ENV
export CKAN_POSTGRES_ADMIN=postgresql://postgres:pass@localhost/postgres
export CKAN_SOLR=http://127.0.0.1:8983/solr

python ./simple_api_testing/run_tests.py
```

(I usually put lines above in a simple bash script, just to make it
easier to remember :))


## Debugging

To compare objects from the debugger, use functions from pytest::

    from ckan_api_client.tests.conftest import diff_eq
