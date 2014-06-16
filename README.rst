Ckan API client
###############

This package provides an improved client for the `ckan <http://ckan.org>`_ API.

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


Installation
============

Latest stable version, from pypi::

    pip install ckan-api-client

Latest from git master::

    pip install http://git.io/ckan-api-client.tar.gz


Example usage
=============

.. code-block:: python

    >>> from ckan_api_client.high_level import CkanHighlevelClient
    >>> from ckan_api_client.objects import CkanDataset

    >>> client = CkanHighlevelClient('http://127.0.0.1:5000', api_key='e70c15cc-2f07-4845-8c6e-3607df88e905')

We don't have datasets yet on our clean instance:

.. code-block:: python

    >>> client.list_datasets()
    []

Let's create a new dataset:

.. code-block:: python

    >>> new_dataset = client.create_dataset(CkanDataset({
    ...     'name': 'example-dataset',
    ...     'title': 'My example dataset'}))

    >>> new_dataset
    CkanDataset({'maintainer': u'', 'name': u'example-dataset', 'author': u'', 'author_email': u'', 'title': 'My example dataset', 'notes': u'', 'owner_org': None, 'private': False, 'maintainer_email': u'', 'url': u'', 'state': u'active', 'extras': {}, 'groups': [], 'license_id': u'', 'type': u'dataset', 'id': u'dfe41b34-5114-47be-8d94-759f942938fc', 'resources': []})

    >>> client.list_datasets()
    [u'dfe41b34-5114-47be-8d94-759f942938fc']

Now, let's change its title:

.. code-block:: python

    >>> new_dataset.title = 'NEW TITLE'

    >>> client.update_dataset(new_dataset)
    CkanDataset({'maintainer': u'', 'name': u'example-dataset', 'author': u'', 'author_email': u'', 'title': 'NEW TITLE', 'notes': u'', 'owner_org': None, 'private': False, 'maintainer_email': u'', 'url': u'', 'state': u'active', 'extras': {}, 'groups': [], 'license_id': u'', 'type': u'dataset', 'id': u'dfe41b34-5114-47be-8d94-759f942938fc', 'resources': []})

Get it back:

.. code-block:: python

    >>> client.get_dataset('dfe41b34-5114-47be-8d94-759f942938fc')
    (same result as above)

Delete it:

.. code-block:: python

    >>> client.wipe_dataset(new_dataset.id)

Trying to get the dataset again will raise a "simulated" 404: Ckan
will never delete datasets, it just marks them as "state: deleted",
for administrative users, and returns a 403 for anonymous ones. We
want to provide more consistency so we raise an exception.

If you **really** want to get the deleted dataset, add
``allow_deleted=True``.

.. code-block:: python

    >>> client.get_dataset('dfe41b34-5114-47be-8d94-759f942938fc')
    HTTPError: HTTPError(404, '(logical) dataset state is deleted', original=None)
