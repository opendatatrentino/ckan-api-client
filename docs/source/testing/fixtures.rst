Fixtures
########

Documentation of the available fixtures for tests.


.. py:module:: ckan_api_client.tests.conftest


Fixture functions
=================

.. autofunction:: ckan_env

.. autofunction:: ckan_instance

.. autofunction:: ckan_url

.. autofunction:: data_dir

.. autofunction:: ckan_client_ll

.. autofunction:: ckan_client_hl

.. autofunction:: ckan_client_sync



Utility objects
===============

.. autoclass:: CkanEnvironment
    :undoc-members:
    :members:

.. autoclass:: CkanInstance
    :undoc-members:
    :members:

.. autoclass:: ConfFileWrapper
    :members:
    :undoc-members:

.. autoclass:: ProcessWrapper
    :members:
    :undoc-members:


Utility functions
=================

Functions used by fixtures.

.. autofunction:: check_tcp_port

.. autofunction:: wait_net_service

.. autofunction:: discover_available_port
