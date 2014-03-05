Clients
#######

There are currently three clients for the Ckan API, each one providing
a different level of abstraction, and thus can be user for different needs:

- :py:class:`CkanLowlevelClient <ckan_api_client.low_level.CkanLowlevelClient>`
  -- just a wrapper around the API.

- High-level client: provides more abstraction around the CRUD methods.

- Syncing client: provides facilities for "syncing" a collection of objects
  into Ckan.


.. toctree::
    :maxdepth: 2
    :glob:

    low-level
    high-level
    syncing
