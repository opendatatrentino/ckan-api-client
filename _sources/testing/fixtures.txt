Fixtures
########

Documentation of the available fixtures for tests.


.. py:module:: ckan_api_client.tests.conftest


Fixture functions
=================

.. autofunction:: ckan_env

.. autofunction:: ckan_url

.. autofunction:: data_dir

.. autofunction:: ckan_client_ll

.. autofunction:: ckan_client_hl

.. autofunction:: ckan_client_sync



Utility objects
===============

.. autoclass:: ckan_api_client.tests.conftest.CkanEnvironment
    :undoc-members:
    :members:
    :exclude-members: __init__, __del__, from_environment, conf_del, conf_get,
        conf_set, conf_update, setup, teardown,
	run_paster, run_paster_with_conf, serve, paster_db_init,
	paster_search_index_rebuild, paster_user_add, paster_user_remove,
	paster_sysadmin_add, paster_sysadmin_remove,

    .. automethod:: __init__
    .. automethod:: from_environment
    .. automethod:: __del__

    **Setup/teardown functions:**

    These functions are automatically called by :py:meth:`__init__`
    and :py:meth:`__del__` and shouldn't be called manually.

    .. automethod:: setup
    .. automethod:: teardown

    **Configuration management:**

    Functions used to manage changes to Ckan configuration file.

    .. automethod:: conf_get
    .. automethod:: conf_set
    .. automethod:: conf_del
    .. automethod:: conf_update

    **Paster commands:**

    .. automethod:: run_paster
    .. automethod:: run_paster_with_conf
    .. automethod:: serve
    .. automethod:: paster_db_init
    .. automethod:: paster_search_index_rebuild
    .. automethod:: paster_user_add
    .. automethod:: paster_user_remove
    .. automethod:: paster_sysadmin_add
    .. automethod:: paster_sysadmin_remove

    **Other functions (mostly for internal use):**


.. autoclass:: CkanServerWrapper
    :members:
    :undoc-members:


Utility functions
=================

Functions used by fixtures.

.. autofunction:: check_tcp_port

.. autofunction:: wait_net_service

.. autofunction:: discover_available_port
