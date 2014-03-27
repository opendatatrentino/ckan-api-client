"""
Synchronization client.


Strategy:

- upsert organizations, get ``{source_id: ckan_id}`` map
- upsert groups, get ``{source_id: ckan_id}`` map
- create collection of CkanDatasets from original dicts
- calculate differences between desired and actual state
- perform syncrhonization
- double-check differences
"""

import copy
import random

from ckan_api_client.exceptions import HTTPError
from ckan_api_client.high_level import CkanHighlevelClient
from ckan_api_client.objects import CkanDataset, CkanOrganization, CkanGroup
from ckan_api_client.utils import IDMap, IDPair


# Extras field containing id of the external source.
# The id is simply source_name:
HARVEST_SOURCE_ID_FIELD = '_harvest_source'


class SynchronizationClient(object):
    """
    Synchronization client, providing functionality for importing
    collections of datasets into a Ckan instance.

    Strategy:

    - find all "own" datasets from Ckan
    - figure out which datasets need insertion/update/deletion
    - apply changes
    """

    def __init__(self, base_url, api_key=None):
        self._client = CkanHighlevelClient(base_url, api_key)

    def sync(self, source_name, data):
        """
        Synchronize data from a source into Ckan.

        :param source_name: string identifying the source
        :param data: data to be synchronized
        """

        groups = dict(
            (key, CkanGroup(val))
            for key, val in data['group'].iteritems())
        organizations = dict(
            (key, CkanOrganization(val))
            for key, val in data['organization'].iteritems())

        # Upsert groups and organizations
        groups_map = self._upsert_groups(groups)
        orgs_map = self._upsert_organizations(organizations)

        # Create list of datasets to be synced
        source_datasets = {}
        for source_id, dataset_dict in data['dataset'].iteritems():
            _dataset_dict = copy.deepcopy(dataset_dict)

            # We need to make sure "source" datasets
            # don't have (otherwise misleading) ids
            _dataset_dict.pop('id', None)

            # We need to update groups and organizations,
            # to map their name from the source into a
            # ckan id
            _dataset_dict['groups'] = [
                groups_map.to_ckan(grp_id)
                for grp_id in _dataset_dict['groups']
            ]
            _dataset_dict['owner_org'] = \
                orgs_map.to_ckan(_dataset_dict['owner_org'])

            dataset = CkanDataset(_dataset_dict)

            # We also want to add the "source id", used for further
            # synchronizations to find stuff
            dataset.extras[HARVEST_SOURCE_ID_FIELD] = \
                self._join_source_id(source_name, source_id)

            source_datasets[source_id] = dataset

        # Retrieve list of datasets from Ckan
        ckan_datasets = self._find_datasets_by_source(source_name)

        # Compare collections to find differences
        differences = self._compare_collections(
            ckan_datasets, source_datasets)

        # ------------------------------------------------------------
        # We now need to create/update/delete datasets.

        # todo: we need to make sure dataset names are not
        #       already used by another dataset. The only
        #       way is to randomize resource names and hope
        #       a 409 response indicates duplicate name..

        # We delete first, in order to (possibly) deallocate
        # some already-used names..
        for source_id in differences['left']:
            ckan_id = ckan_datasets[source_id].id
            self._client.delete_dataset(ckan_id)

        def force_dataset_operation(operation, dataset, retry=5):
            # Maximum dataset name length is 100 characters
            # We trim it down to 80 just to be safe.
            _orig_name = dataset.name[:80]
            dataset.name = _orig_name
            while True:
                try:
                    result = operation(dataset)
                except HTTPError, e:
                    if e.status_code != 409:
                        raise
                    retry -= 1
                    if retry < 0:
                        raise
                    dataset.name = '{0}-{1:06d}'.format(
                        _orig_name,
                        random.randint(0, 999999))
                else:
                    return result

        # Create missing datasets
        for source_id in differences['right']:
            dataset = source_datasets[source_id]
            force_dataset_operation(self._client.create_dataset, dataset)

        # Update outdated datasets
        for source_id in differences['differing']:
            dataset = source_datasets[source_id]
            dataset.id = ckan_datasets[source_id].id
            # self._client.update_dataset(dataset)
            force_dataset_operation(self._client.update_dataset, dataset)

        # Todo: double-check differences?

    # def _sync_datasets(self, source_name, datasets):
    #     """
    #     Synchronize datasets into Ckan.

    #     :param source_name:
    #         Name of the data source
    #     :param datasets:
    #         Dictionary mapping ``source_id: CkanDataset()``
    #     """
    #     pass

    def _upsert_groups(self, groups):
        """
        :param groups:
            dict mapping ``{org_name : CkanGroup()}``
        :return: a map of source/ckan ids of groups
        :rtype: IDMap
        """

        idmap = IDMap()

        for group_name, group in groups.iteritems():
            if not isinstance(group, CkanGroup):
                raise TypeError("Expected CkanGroup, got {0!r}"
                                .format(type(group)))

            if group.name != group_name:
                raise ValueError("Mismatching group name!")

            try:
                ckan_group = self._client.get_group_by_name(
                    group_name, allow_deleted=True)

            except HTTPError, e:
                if e.status_code != 404:
                    raise

                # We need to create the group
                group.id = None
                group.state = 'active'
                created_group = self._client.create_group(group)
                idmap.add(IDPair(source_id=group.name,
                                 ckan_id=created_group.id))

            else:
                # The group already exist. It might be logically
                # deleted, but we don't care -> just update and
                # make sure it is marked as active.

                # todo: make sure we don't need to preserve users and stuff,
                #       otherwise we need to workaround that in hi-lev client

                group.id = ckan_group.id
                group.state = 'active'
                updated_group = self._client.update_group(group)
                idmap.add(IDPair(source_id=group.name,
                                 ckan_id=updated_group.id))

        return idmap

    def _upsert_organizations(self, orgs):
        """
        :param orgs:
            dict mapping ``{org_name : CkanOrganization()}``
        :return: a map of source/ckan ids of organizations
        :rtype: IDMap
        """

        idmap = IDMap()

        for org_name, org in orgs.iteritems():
            if not isinstance(org, CkanOrganization):
                raise TypeError("Expected CkanOrganization, got {0!r}"
                                .format(type(org)))

            if org.name != org_name:
                raise ValueError("Mismatching org name!")

            try:
                ckan_org = self._client.get_organization_by_name(
                    org_name, allow_deleted=True)

            except HTTPError, e:
                if e.status_code != 404:
                    raise

                # We need to create the org
                org.id = None
                org.state = 'active'
                created_org = self._client.create_organization(org)
                idmap.add(IDPair(source_id=org.name,
                                 ckan_id=created_org.id))

            else:
                org.id = ckan_org.id
                org.state = 'active'
                updated_org = self._client.update_organization(org)
                idmap.add(IDPair(source_id=org.name,
                                 ckan_id=updated_org.id))

        return idmap

    def _find_datasets_by_source(self, source_name):
        """
        Find all datasets matching the current source.
        Returns a dict mapping source ids with dataset objects.
        """

        results = {}
        for dataset in self._client.iter_datasets():
            if HARVEST_SOURCE_ID_FIELD not in dataset.extras:
                continue
            source_id = dataset.extras[HARVEST_SOURCE_ID_FIELD]
            _name, _id = self._parse_source_id(source_id)
            if _name == source_name:
                results[_id] = dataset
        return results

    def _parse_source_id(self, source_id):
        splitted = source_id.split(':')
        if len(splitted) != 2:
            raise ValueError("Invalid source id")
        return splitted

    def _join_source_id(self, source_name, source_id):
        return ':'.join((source_name, source_id))

    def _compare_collections(self, left, right):
        """
        Compare two collections of objects.

        Both collections are dictionaries mapping "source" ids
        with objects.

        :param left:
            The "original" collection, retrieved from Ckan.
            Objects will already have ids.

        ``left`` is the collection retrieved

        The two collections are simply dictionaries of objects;
        keys are the ids (used internally by the source).
        Values in the right will contain Ckan ids, while the ones
        in the left will not.

        :returns:
            A dictionary mapping names to sets of keys:

            * ``common`` -- keys in both mappings
            * ``differing`` -- keys of differing objects
            * ``left`` -- keys of objects that are only in ckan
            * ``right`` -- keys of objects that are not in ckan
        """

        left_keys = set(left.iterkeys())
        right_keys = set(right.iterkeys())

        common_keys = left_keys & right_keys
        left_only_keys = left_keys - right_keys
        right_only_keys = right_keys - left_keys

        differing = set(k for k in common_keys if left[k] != right[k])

        return {
            'common': common_keys,
            'left': left_only_keys,
            'right': right_only_keys,
            'differing': differing,
        }
