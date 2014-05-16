Ckan API client
###############

This package provides a client for the `ckan <http://ckan.org>`_ API.

Specifically, it includes:

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


Documentation
=============

Documentation is available on Read The Docs:

http://ckan-api-client.readthedocs.org

a mirror copy is currently available on GitHub pages:

https://opendatatrentino.github.io/ckan-api-client/


Example usage
=============

.. code-block:: python

    from ckan_api_client.high_level import CkanHighlevelClient
