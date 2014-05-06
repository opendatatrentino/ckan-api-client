import random
import string

from .objects import CkanDataset, CkanOrganization, CkanGroup
from .low_level import CkanLowlevelClient
from .exceptions import OperationFailure, HTTPError


class CkanHighlevelClient(object):
    """
    High-level client, handling CRUD of objects.

    This class only returns / handles CkanObjects, to make sure
    we are handling consistent data (they have validators in place)
    """

    def __init__(self, base_url, api_key=None):
        self._client = CkanLowlevelClient(base_url, api_key)

    # ------------------------------------------------------------
    # Datasets management
    # ------------------------------------------------------------

    def list_datasets(self):
        """:return: a list of dataset ids"""
        return self._client.list_datasets()

    def iter_datasets(self):
        """Generator, iterating over all the datasets in ckan"""
        for id in self.list_datasets():
            yield self.get_dataset(id)

    def get_dataset(self, id, allow_deleted=False):
        """
        Get a specific dataset, by id

        .. note::

            Since the Ckan API use both ids and names as keys,
            both :py:meth:`get_dataset` and :py:meth:`get_dataset_by_name`
            will perform the exact same request in the background.

            The difference is only in the high-level handling:
            the function will check whether the expected id has the correct
            value, and raise an HTTPError(404, ..) otherwise..

        :param str id:
            the dataset id
        :param allow_deleted:
            Whether to return even logically deleted objects.
            If set to ``False`` (the default) will raise a
            ``HTTPError(404, ..)`` if ``state != 'active'``
        :rtype: :py:class:`CkanDataset <.objects.ckan_dataset.CkanDataset>`
        """

        data = self._client.get_dataset(id)

        if data['id'] != id:
            raise HTTPError(404, '(logical) dataset id mismatch')

        if not (allow_deleted or data['state'] == 'active'):
            raise HTTPError(404, '(logical) dataset state is deleted')

        return CkanDataset(data)

    def get_dataset_by_name(self, name, allow_deleted=False):
        """
        Get a specific dataset, by name

        .. note:: See note on :py:meth:`get_dataset`

        :param str name:
            the dataset name
        :param allow_deleted:
            Whether to return even logically deleted objects.
            If set to ``False`` (the default) will raise a
            ``HTTPError(404, ..)`` if ``state != 'active'``
        :rtype: :py:class:`CkanDataset <.objects.ckan_dataset.CkanDataset>`
        """

        data = self._client.get_dataset(name)

        if data['name'] != name:
            raise HTTPError(404, '(logical) dataset name mismatch')

        if not (allow_deleted or data['state'] == 'active'):
            raise HTTPError(404, '(logical) dataset state is deleted')

        return CkanDataset(data)

    def save_dataset(self, dataset):
        """
        If the dataset already has an id, call :py:meth:`update_dataset`,
        otherwise, call :py:meth:`create_dataset`.

        :return: as returned by the called function.
        :rtype: :py:class:`CkanDataset <.objects.ckan_dataset.CkanDataset>`
        """

        if not isinstance(dataset, CkanDataset):
            raise TypeError("Dataset must be a CkanDataset")

        if dataset.id is not None:
            return self.update_dataset(dataset)
        return self.create_dataset(dataset)

    def create_dataset(self, dataset):
        """
        Create a dataset

        :rtype: :py:class:`CkanDataset <.objects.ckan_dataset.CkanDataset>`
        """

        if not isinstance(dataset, CkanDataset):
            raise TypeError("dataset must be a CkanDataset")
        if dataset.id is not None:
            raise ValueError("Cannot specify an id when creating an object")

        data = self._client.post_dataset(dataset.serialize())
        created = CkanDataset(data)

        if not created.is_equivalent(dataset):
            raise OperationFailure("Created dataset doesn't match")

        return created

    def update_dataset(self, dataset):
        """
        Update a dataset

        :rtype: :py:class:`CkanDataset <.objects.ckan_dataset.CkanDataset>`
        """

        if not isinstance(dataset, CkanDataset):
            raise TypeError("Dataset must be a CkanDataset")
        if dataset.id is None:
            raise ValueError("Trying to update a dataset without an id")

        # ------------------------------------------------------------
        # We need the original dataset to make sure
        # we are updating things correctly.

        original_dataset = self.get_dataset(dataset.id)
        updates_dict = dataset.serialize()

        # ------------------------------------------------------------
        # Process the Extras field

        # In order to remove an "extras" field, we need to
        # explicitly set its value to None

        # todo: we should track changes on the "extras" field in order
        #       to make sure we aren't accidentally removing fields
        #       that have been added in the meanwhile..

        for key in original_dataset.extras:
            if key not in updates_dict['extras']:
                updates_dict['extras'][key] = None

        # ------------------------------------------------------------
        # Actually send HTTP request to update the dataset
        data = self._client.put_dataset(updates_dict)
        updated = CkanDataset(data)

        # Make sure the returned dataset matches the desired state
        if not updated.is_equivalent(dataset):
            raise OperationFailure("Updated dataset doesn't match")

        return updated

    def delete_dataset(self, id):
        """Delete a dataset, by id"""
        self._client.delete_dataset(id)

    def wipe_dataset(self, id):
        """Actually delete a dataset, by renaming it first"""
        dataset = self.get_dataset(id)
        chars = string.ascii_lowercase + string.digits
        dataset.name = 'deleted-{0}'.format(''.join(
            random.choice(chars) for i in xrange(10)))
        self.update_dataset(dataset)
        self.delete_dataset(id)

    # ------------------------------------------------------------
    # Organizations management
    # ------------------------------------------------------------

    def list_organizations(self):
        return [
            self.get_organization_by_name(name).id
            for name in self.list_organization_names()
        ]

    def list_organization_names(self):
        return self._client.list_organizations()

    def iter_organizations(self):
        for name in self.list_organization_names():
            yield self.get_organization_by_name(name)

    def get_organization(self, id, allow_deleted=False):
        """
        Get organization, by id.

        .. note:: See note on :py:meth:`get_dataset`

        :param str id:
            the organization id
        :param allow_deleted:
            Whether to return even logically deleted objects.
            If set to ``False`` (the default) will raise a
            ``HTTPError(404, ..)`` if ``state != 'active'``
        :rtype: :py:class:`CkanOrganization
            <.objects.ckan_organization.CkanOrganization>`
        """

        data = self._client.get_organization(id)

        if data['id'] != id:
            raise HTTPError(404, '(logical) organization id mismatch')

        if not (allow_deleted or data['state'] == 'active'):
            raise HTTPError(404, '(logical) organization state is deleted')

        if 'extras' in data:
            data['extras'] = _destupidize_dict(data['extras'])

        return CkanOrganization(data)

    def get_organization_by_name(self, name, allow_deleted=False):
        """
        Get organization by name.

        .. note:: See note on :py:meth:`get_dataset`

        :param str name:
            the organization name
        :param allow_deleted:
            Whether to return even logically deleted objects.
            If set to ``False`` (the default) will raise a
            ``HTTPError(404, ..)`` if ``state != 'active'``
        :rtype: :py:class:`CkanOrganization
            <.objects.ckan_organization.CkanOrganization>`
        """

        data = self._client.get_organization(name)

        if data['name'] != name:
            raise HTTPError(404, '(logical) organization name mismatch')

        if not (allow_deleted or data['state'] == 'active'):
                raise HTTPError(404, '(logical) organization state is deleted')

        if 'extras' in data:
            data['extras'] = _destupidize_dict(data['extras'])

        return CkanOrganization(data)

    def save_organization(self, organization):
        if not isinstance(organization, CkanOrganization):
            raise TypeError("Organization must be a CkanOrganization")

        if organization.id is not None:
            return self.update_organization(organization)
        return self.create_organization(organization)

    def create_organization(self, organization):
        """
        Create an organization

        :rtype: :py:class:`CkanOrganization
            <.objects.ckan_organization.CkanOrganization>`
        """

        if not isinstance(organization, CkanOrganization):
            raise TypeError("Organization must be a CkanOrganization")
        if organization.id is not None:
            raise ValueError("Cannot specify an id when creating an object")

        serialized = organization.serialize()
        if 'extras' in serialized:
            serialized['extras'] = _stupidize_dict(serialized['extras'])

        data = self._client.post_organization(serialized)

        if 'extras' in data:
            data['extras'] = _destupidize_dict(data['extras'])

        created = CkanOrganization(data)

        if not created.is_equivalent(organization):
            raise OperationFailure("Created organization doesn't match")

        return created

    def update_organization(self, organization):
        """
        :rtype: :py:class:`CkanOrganization
            <.objects.ckan_organization.CkanOrganization>`
        """
        if not isinstance(organization, CkanOrganization):
            raise TypeError("Organization must be a CkanOrganization")
        if organization.id is None:
            raise ValueError("Trying to update a organization without an id")

        serialized = organization.serialize()
        if 'extras' in serialized:
            serialized['extras'] = _stupidize_dict(serialized['extras'])

        data = self._client.put_organization(serialized)

        if 'extras' in data:
            data['extras'] = _destupidize_dict(data['extras'])

        updated = CkanOrganization(data)

        if not updated.is_equivalent(organization):
            raise OperationFailure("Updated organization doesn't match")

        return updated

    def delete_organization(self, id):
        self._client.delete_organization(id)

    # ------------------------------------------------------------
    # Groups management
    # The list from the API is at /api/2/rest/group and it will
    # correctly return group ids.
    # ------------------------------------------------------------

    def list_groups(self):
        return self._client.list_groups()

    def list_group_names(self):
        return [
            self.get_group(id).name
            for id in self.list_groups()
        ]

    def iter_groups(self):
        for id in self.list_groups():
            yield self.get_group(id)

    def get_group(self, id, allow_deleted=False):
        """
        Get group, by id.

        .. note:: See note on :py:meth:`get_dataset`

        :param str id:
            the group id
        :param allow_deleted:
            Whether to return even logically deleted objects.
            If set to ``False`` (the default) will raise a
            ``HTTPError(404, ..)`` if ``state != 'active'``
        :rtype: :py:class:`CkanGroup <.objects.ckan_group.CkanGroup>`
        """

        data = self._client.get_group(id)

        if data['id'] != id:
            raise HTTPError(404, '(logical) group id mismatch')

        if not (allow_deleted or data['state'] == 'active'):
            raise HTTPError(404, '(logical) group state is deleted')

        return CkanGroup(data)

    def get_group_by_name(self, name, allow_deleted=False):
        """
        Get group by name.

        .. note:: See note on :py:meth:`get_dataset`

        :param str name:
            the group name
        :param allow_deleted:
            Whether to return even logically deleted objects.
            If set to ``False`` (the default) will raise a
            ``HTTPError(404, ..)`` if ``state != 'active'``
        :rtype: :py:class:`CkanGroup <.objects.ckan_group.CkanGroup>`
        """

        data = self._client.get_group(name)

        if data['name'] != name:
            raise HTTPError(404, '(logical) group name mismatch')

        if not (allow_deleted or data['state'] == 'active'):
                raise HTTPError(404, '(logical) group state is deleted')

        return CkanGroup(data)

    def save_group(self, group):
        if not isinstance(group, CkanGroup):
            raise TypeError("Group must be a CkanGroup")

        if group.id is not None:
            return self.update_group(group)
        return self.create_group(group)

    def create_group(self, group):
        """
        :rtype: :py:class:`CkanGroup <.objects.ckan_group.CkanGroup>`
        """
        if not isinstance(group, CkanGroup):
            raise TypeError("Group must be a CkanGroup")
        if group.id is not None:
            raise ValueError("Cannot specify an id when creating an object")

        data = self._client.post_group(group.serialize())
        created = CkanGroup(data)

        if not created.is_equivalent(group):
            raise OperationFailure("Created group doesn't match")

        return created

    def update_group(self, group):
        """
        :rtype: :py:class:`CkanGroup <.objects.ckan_group.CkanGroup>`
        """
        if not isinstance(group, CkanGroup):
            raise TypeError("Group must be a CkanGroup")
        if group.id is None:
            raise ValueError("Trying to update a group without an id")

        data = self._client.put_group(group.serialize())
        updated = CkanGroup(data)

        if not updated.is_equivalent(group):
            raise OperationFailure("Updated group doesn't match")

        return updated

    def delete_group(self, id):
        return self._client.delete_group(id)


# ------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------

def _stupidize_dict(mydict):
    """Convert a dictionary to a list of ``{key: ..., value: ...}``"""
    return [
        {'key': key, 'value': value} for key, value in mydict.iteritems()
    ]


def _destupidize_dict(mylist):
    """The opposite of _stupidize_dict()"""
    output = {}
    for item in mylist:
        output[item['key']] = item['value']
    return output
