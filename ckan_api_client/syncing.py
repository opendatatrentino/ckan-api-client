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

from ckan_api_client.high_level import CkanHighlevelClient
from ckan_api_client.objects import CkanDataset, CkanOrganization, CkanGroup
from ckan_api_client.utils import IDMap, IDPair


## Extras field containing id of the external source.
## The id is simply source_name:
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

        ## Upsert groups adn organizations
        groups_map = self._upsert_groups(data['group'])
        orgs_map = self._upsert_organizations(data['organization'])

        ## Create list of datasets to be synced
        source_datasets = {}
        for source_id, dataset_dict in data['dataset']:
            _dataset_dict = copy.deepcopy(dataset_dict)

            ## We need to make sure "source" datasets
            ## don't have (otherwise misleading) ids
            _dataset_dict.pop('id', None)

            ## We need to update groups and organizations,
            ## to map their name from the source into a
            ## ckan id
            _dataset_dict['groups'] = [
                groups_map.to_ckan(grp_id)
                for grp_id in _dataset_dict['groups']
            ]
            _dataset_dict['owner_org'] = \
                orgs_map.to_ckan(_dataset_dict['owner_org'])

            dataset = CkanDataset(_dataset_dict)

            ## We also want to add the "source id", used for further
            ## synchronizations to find stuff
            dataset.extras[HARVEST_SOURCE_ID_FIELD] = \
                '{0}:{1}'.format(source_name, source_id)

            source_datasets[source_id] = CkanDataset(dataset)

        ## Retrieve list of datasets from Ckan
        ckan_datasets = self.get_datasets_by_source(source_name)

        ## Compare collections to find differences
        differences = self.compare_collections(
            ckan_datasets, source_datasets)

        ##------------------------------------------------------------
        ## We now need to create/update/delete datasets.

        ## todo: we need to make sure dataset names are not
        ##       already used by another dataset. The only
        ##       way is to randomize resource names and hope
        ##       a 409 response indicates duplicate name..

        ## We delete first, in order to (possibly) deallocate
        ## some already-used names..
        for source_id in differences['left']:
            ckan_id = ckan_datasets[source_id].id
            self._client.delete_dataset(ckan_id)

        ## Create missing datasets
        for source_id in differences['right']:
            dataset = source_datasets[source_id]
            self._client.create_dataset(dataset)

        for source_id in differences['differing']:
            pass
        pass

    def _sync_datasets(self, source_name, datasets):
        """
        Synchronize datasets into Ckan.

        :param source_name:
            Name of the data source
        :param datasets:
            Dictionary mapping ``source_id: CkanDataset()``
        """
        pass

    def _upsert_groups(self, groups):
        """
        Upsert a list of groups into Ckan.

        :param groups:
            a dict mapping ``name: CkanGroup()``
        """
        pass

    def _upsert_organizations(self, organizations):
        pass

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
            if _name == source_id:
                results[_id] = dataset
        return results

    def _parse_source_id(self, source_id):
        splitted = source_id.split(':')
        if len(splitted) != 2:
            raise ValueError("Invalid source id")
        return splitted

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
