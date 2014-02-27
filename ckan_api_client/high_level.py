"""
High-level client for Ckan API
"""

import copy
import warnings

from .low_level import CkanLowlevelClient
from .high_level import DATASET_FIELDS, RESOURCE_FIELDS


class CkanHighlevelClient(object):
    def __init__(self, base_url, api_key=None):
        self._client = CkanLowlevelClient(base_url, api_key)

    ##------------------------------------------------------------
    ## Datasets management
    ##------------------------------------------------------------

    def list_datasets(self):
        """Return a list of dataset ids"""
        return self._client.list_datasets()

    def iter_datasets(self, cleanup=False):
        """Generator yielding dataset objects from Ckan"""
        for dataset_id in self.list_datasets():
            yield self.read_dataset(dataset_id, cleanup=cleanup)

    def create_dataset(self, dataset, cleanup=False):
        """Create a dataset into Ckan"""
        if 'id' in dataset:
            raise ValueError(
                "Attempring to created a dataset while already specifying "
                "an id. This might lead to unexpected behavior, so it is "
                "disallowed.")

        ## Don't change the original dataset!
        dataset = copy.deepcopy(dataset)

        ## Validate and clean the dataset
        self._validate_dataset(dataset)

        ## Actually put the dataset to Ckan
        result = self._client.post_dataset(dataset)

        ## Clean up the dataset
        if cleanup:
            self._cleanup_dataset(result)

        return result

    def _validate_dataset(self, dataset):
        """
        Validate / cleanup a dataset.

        .. warning:: original dataset will be modified in place!
        """
        keys_to_remove = set()

        for key, value in dataset.iteritems():
            if key in DATASET_FIELDS['core']:
                continue  # Ok..

            elif key in DATASET_FIELDS['cruft']:
                warnings.warn("You passed the {0} field, which is a cruft "
                              "field. We're removing it, but don't do it "
                              "again!".format(key))
                keys_to_remove.add(key)

            elif key in DATASET_FIELDS['special']:
                continue  # Handled later..

            else:
                warnings.warn("You passed an unknown field {0}. Removing it "
                              "now, but you'd better investingate.."
                              .format(key))
                keys_to_remove.add(key)

        for key in keys_to_remove:
            del dataset[key]

        if 'extras' in dataset:
            self._validate_dataset_extras(dataset['extras'])

        if 'groups' in dataset:
            if not isinstance(dataset['groups'], list):
                raise TypeError("Dataset groups must be a list")

            if not all(isinstance(x, basestring) for x in dataset['groups']):
                raise TypeError("Dataset groups must be a list of strings")

        if ('relationships' in dataset) and dataset['resources']:
            raise NotImplementedError("Relationships are not supported yet.")

        if 'resources' in dataset:
            self._validate_dataset_resources(dataset['resources'])

    def _validate_dataset_resources(self, resources):
        """
        Validate dataset resources.

        .. warning::
            Resources will be modified in place to remove
            certain fields..
        """
        for resource in resources:
            ## Validate core / cruft fields
            res_keys_to_remove = set()
            for res_key, res_value in resource.iteritems():
                if res_key in RESOURCE_FIELDS['core']:
                    continue

                elif res_key in RESOURCE_FIELDS['cruft']:
                    warnings.warn(
                        "You passed the {0} resource field, which is "
                        "listed as cruft. We're removing it now, but "
                        "don't do it again!")
                    res_keys_to_remove.add(res_key)

                else:
                    warnings.warn(
                        "You passed an unknown resource field {0}. "
                        "Removing it now, but you'd better "
                        "investigate..".format(res_key))
                    res_keys_to_remove.add(res_key)

            for res_key in res_keys_to_remove:
                del resource[res_key]

    def _validate_dataset_extras(self, extras):
        """
        Validate an 'extras' dict.

        Basically, this will check that the passed-in argument
        is a dict mapping strings to strings.
        """

        if not isinstance(extras, dict):
            raise TypeError("Dataset extras must be a dict")

        for key, value in extras.iteritems():
            if not isinstance(key, basestring):
                raise TypeError("Extras keys must be strings")
            if not isinstance(value, basestring):
                raise TypeError("Extras values must be strings")

    def _cleanup_dataset(self, dataset):
        """
        Cleanup a dataset returned from the API.

        .. warning:: dataset will be modified in place
        """

        ## Remove invalid fields
        ##----------------------------------------

        valid_fields = set()
        valid_fields.update(DATASET_FIELDS['core'])
        valid_fields.update(DATASET_FIELDS['keys'])
        valid_fields.update(DATASET_FIELDS['special'])

        fields_to_remove = set()
        for key in dataset:
            if key in DATASET_FIELDS['cruft']:
                fields_to_remove.add(key)
            elif key not in valid_fields:
                warnings.warn("Unexpected field returned by the API: {0}"
                              .format(key))
                fields_to_remove.add(key)
        for key in fields_to_remove:
            del dataset[key]

        ## Make sure special fields are all there
        if 'resources' not in dataset:
            dataset['resources'] = []
        if 'groups' not in dataset:
            dataset['groups'] = []
        if 'extras' not in dataset:
            dataset['extras'] = {}

        ## Clean up resources too..
        ##----------------------------------------

        valid_resource_fields = set()
        valid_resource_fields.update(RESOURCE_FIELDS['core'])
        valid_resource_fields.update(RESOURCE_FIELDS['keys'])
        valid_resource_fields.update(RESOURCE_FIELDS['special'])

        for resource in dataset['resources']:
            fields_to_remove = set()
            for key in resource:
                if key in DATASET_FIELDS['cruft']:
                    fields_to_remove.add(key)
                elif key not in valid_resource_fields:
                    warnings.warn("Unexpected resource field returned "
                                  "by the API: {0}".format(key))
                    fields_to_remove.add(key)
            for key in fields_to_remove:
                del resource[key]

    def read_dataset(self, id, cleanup=False):
        result = self._client.get_dataset(id)
        if cleanup:
            self._cleanup_dataset(result)
        return result

    def update_dataset(self, id, dataset):
        if 'id' in dataset:
            if dataset['id'] != id:
                raise ValueError("Mismatching ids")

        ## We need this as a reference
        original_dataset = self.read_dataset(id, cleanup=True)

        ## Make sure updates dictionary is clean
        self._validate_dataset(dataset)

        ## Make sure we have all the core fields
        for field in DATASET_FIELDS['core']:
            if field not in dataset:
                dataset[field] = original_dataset[field]

        ## Merge extras
        extras = copy.deepcopy(original_dataset['extras'])
        if 'extras' in dataset:
            extras.update(dataset['extras'])
        dataset['extras'] = extras

        ## Set groups (keep the old ones if omitted)
        if 'groups' not in dataset:
            dataset['groups'] = original_dataset['groups']

        if 'resources' in dataset:
            dataset['resources'] = self._merge_resources(original, updated)
        else:
            dataset['resources'] = []

    def _merge_resources(original, updated):
        """
        We want to replace resources listed in "original" with the ones
        listed in "updated".

        Strategy here is: if a resource with the same url exists, keep
        its id for update. Otherwise, just create a new one and forget
        about the old one.
        """
        pass

    def delete_dataset(self, id):
        pass
