# Ckan API client

Python client for [Ckan](http://ckan.org) API.

This package provides:

- a low-level client, which is pretty much just a wrapper around
  HTTP calls, handling serialization and exception-raising.

- a high-level client, attempting to make it easier / safer to perform
  certain operations on a ckan catalog.

- a "syncing" client, used to provide some automation for synchronization
  tasks of collections of datasets (commonly referred to as "harvesting").


## Documentation

Coming soon. Keep tuned.


## Running tests

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
