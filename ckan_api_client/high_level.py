from .objects import CkanDataset, CkanOrganization, CkanGroup
from .low_level import CkanLowlevelClient
from .exceptions import OperationFailure


class CkanHighlevelClient(object):
    """
    High-level client, handling CRUD of objects.

    This class only returns / handles CkanObjects, to make sure
    we are handling consistent data (they have validators in place)
    """

    def __init__(self, base_url, api_key=None):
        self._client = CkanLowlevelClient(base_url, api_key)

    ##------------------------------------------------------------
    ## Datasets management
    ##------------------------------------------------------------

    def list_datasets(self):
        """:return: a list of dataset ids"""
        return self._client.list_datasets()

    def iter_datasets(self):
        """Generator, iterating over all the datasets in ckan"""
        for id in self.list_datasets():
            yield self.get_dataset(id)

    def get_dataset(self, id):
        """
        Get a specific dataset, by id

        :rtype: :py:class:`.objects.CkanDataset`
        """

        data = self._client.get_dataset(id)
        return CkanDataset.from_dict(data)

    def save_dataset(self, dataset):
        """
        If the dataset already has an id, call :py:meth:`update_dataset`,
        otherwise, call :py:meth:`create_dataset`.

        :return: as returned by the called function.
        :rtype: :py:class:`.objects.CkanDataset`
        """

        if not isinstance(dataset, CkanDataset):
            raise TypeError("Dataset must be a CkanDataset")

        if dataset.id is not None:
            return self.update_dataset(dataset)
        return self.create_dataset(dataset)

    def create_dataset(self, dataset):
        """
        Create a dataset

        :rtype: :py:class:`.objects.CkanDataset`
        """

        if not isinstance(dataset, CkanDataset):
            raise TypeError("dataset must be a CkanDataset")
        if dataset.id is not None:
            raise ValueError("Cannot specify an id when creating an object")

        data = self._client.post_dataset(dataset.to_dict())
        created = CkanDataset.from_dict(data)

        if not created.is_equivalent(dataset):
            raise OperationFailure("Created dataset doesn't match")

        return created

    def update_dataset(self, dataset):
        """
        Update a dataset

        :rtype: :py:class:`.objects.CkanDataset`
        """

        if not isinstance(dataset, CkanDataset):
            raise TypeError("Dataset must be a CkanDataset")
        if dataset.id is None:
            raise ValueError("Trying to update a dataset without an id")

        data = self._client.put_dataset(dataset.to_dict())
        updated = CkanDataset.from_dict(data)

        if not updated.is_equivalent(dataset):
            raise OperationFailure("Updated dataset doesn't match")

        return updated

    def delete_dataset(self, id):
        """Delete a dataset, by id"""
        self._client.delete_dataset(id)

    ##------------------------------------------------------------
    ## Organizations management
    ##------------------------------------------------------------

    def list_organizations(self):
        return self._client.list_organizations()

    def iter_organizations(self):
        for id in self.list_organizations():
            yield self.get_organization(id)

    def get_organization(self, id):
        data = self._client.get_organization(id)
        return CkanOrganization.from_dict(data)

    def save_organization(self, organization):
        if not isinstance(organization, CkanOrganization):
            raise TypeError("Organization must be a CkanOrganization")

        if organization.id is not None:
            return self.update_organization(organization)
        return self.create_organization(organization)

    def create_organization(self, organization):
        if not isinstance(organization, CkanOrganization):
            raise TypeError("Organization must be a CkanOrganization")
        if organization.id is not None:
            raise ValueError("Cannot specify an id when creating an object")

        data = self._client.post_organization(organization.to_dict())
        created = CkanOrganization.from_dict(data)

        if not created.is_equivalent(organization):
            raise OperationFailure("Created organization doesn't match")

        return created

    def update_organization(self, organization):
        if not isinstance(organization, CkanOrganization):
            raise TypeError("Organization must be a CkanOrganization")
        if organization.id is None:
            raise ValueError("Trying to update a organization without an id")

        data = self._client.put_organization(organization.to_dict())
        updated = CkanDataset.from_dict(data)

        if not updated.is_equivalent(organization):
            raise OperationFailure("Updated organization doesn't match")

        return updated

    def delete_organization(self, id):
        self._client.delete_organization(id)

    ##------------------------------------------------------------
    ## Groups management
    ##------------------------------------------------------------

    def list_groups(self):
        return self._client.list_groups()

    def iter_groups(self):
        for id in self.list_groups():
            yield self.get_group(id)

    def get_group(self, id):
        data = self._client.get_group(id)
        return CkanGroup.from_dict(data)

    def save_group(self, group):
        if not isinstance(group, CkanGroup):
            raise TypeError("Group must be a CkanGroup")

        if group.id is not None:
            return self.update_group(group)
        return self.create_group(group)

    def create_group(self, group):
        if not isinstance(group, CkanGroup):
            raise TypeError("Group must be a CkanGroup")
        if group.id is not None:
            raise ValueError("Cannot specify an id when creating an object")

        data = self._client.post_group(group.to_dict())
        created = CkanGroup.from_dict(data)

        if not created.is_equivalent(group):
            raise OperationFailure("Created group doesn't match")

        return created

    def update_group(self, group):
        if not isinstance(group, CkanGroup):
            raise TypeError("Group must be a CkanGroup")
        if group.id is None:
            raise ValueError("Trying to update a group without an id")

        data = self._client.put_group(group.to_dict())
        updated = CkanGroup.from_dict(data)

        if not updated.is_equivalent(group):
            raise OperationFailure("Updated group doesn't match")

        return updated

    def delete_group(self, id):
        return self._client.delete_group(id)
