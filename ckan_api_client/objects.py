"""
Classes to represent / validate Ckan objects
"""

import collections
import copy

from .schema import DATASET_FIELDS, RESOURCE_FIELDS


class CkanObject(object):
    pass


class CkanDataset(CkanObject):

    # todo: we need to implement comparison

    def __init__(self):
        self._original = {
            'id': None,
            'core': {},
            'extras': {},
            'groups': [],
            'relationships': [],
        }
        self._updates = {'core': {}}
        self._resources = CkanDatasetResources()

    @classmethod
    def from_dict(cls, obj):
        new_obj = cls()

        if 'id' in obj:
            new_obj._original['id'] = obj['id']

        for field in DATASET_FIELDS['core']:
            if field in obj:
                value = obj[field]
                if not isinstance(value, basestring):
                    raise ValueError("Core fields must be strings!")
                new_obj._original['core'][field] = value

        for field in DATASET_FIELDS['special']:
            if field == 'resources':
                continue
            if field in obj:
                ## Just copy them over, we'll handle them
                ## later, if needed..
                new_obj._original[field] = obj[field]

        if 'resources' in obj:
            for res in obj['resources']:
                new_obj._resources.append(
                    CkanResource.from_dict(res))

        return new_obj

    def to_dict(self):
        """Serialize the object as a dictionary"""

        object_as_dict = {}

        object_as_dict['id'] = self.id

        for field in DATASET_FIELDS['core']:
            ## These are strings, no need to copy
            object_as_dict[field] = getattr(self, field)

        for field in ('extras', 'groups', 'relationships'):
            ## Deepcopy special fields, to prevent them from
            ## being altered in the object.
            object_as_dict[field] = copy.deepcopy(getattr(self, field))

        object_as_dict['resources'] = []
        for resource in self._resources:
            object_as_dict['resources'].append(resource.to_dict())

        return object_as_dict

    def is_modified(self):
        if self._updates['core'] != {}:
            return True  # something has been updated
        for field in ('groups', 'extras', 'resources'):
            if (field in self._updates) and \
                    (self._updates[field] != self._original[field]):
                return True
        if self._resources.is_modified():
            return True
        return False

    def __getattr__(self, name):
        if name == 'id':
            # This cannot be updated -- no CoW
            return self._original['id']

        if name in DATASET_FIELDS['core']:
            # CoW :)
            if name in self._updates['core']:
                return self._updates['core'][name]
            return self._original['core'].get(name)

        if name == 'groups':
            return self._get_groups()

        if name == 'extras':
            return self._get_extras()

        if name == 'relationships':
            return self._get_relationships()

        if name == 'resources':
            ## Just to disallow assignment / replacement..
            return self._resources

        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in ['_original', '_updates', '_resources']:
            self.__dict__[name] = value
            return

        if name == 'id':
            raise RuntimeError("Cannot alter value of a field used as a key!")

        if name in DATASET_FIELDS['core']:
            if not isinstance(value, basestring):
                raise TypeError("Core fields must be strings")
            self._updates['core'][name] = value
            return

        ## todo: allow direct assignment of groups / extras?
        ## but, we need to validate carefully..

        if name in DATASET_FIELDS['special']:
            raise RuntimeError(
                "This field cannot be updated directly at once")

        raise AttributeError(name)

    def __delattr__(self, name):
        raise RuntimeError("Cannot delete attribute")

    def _get_from_updates(self, objname):
        if objname not in self._updates:
            self._updates[objname] = copy.deepcopy(self._original[objname])
        return self._updates[objname]

    def _get_groups(self):
        return self._get_from_updates('groups')

    def _get_extras(self):
        return self._get_from_updates('extras')

    def _get_relationships(self):
        return self._get_from_updates('relationships')


class CkanDatasetResources(collections.MutableSequence):
    """Hold a collection of resources"""

    _modified = False

    def __init__(self):
        self._resources = []

    def __getitem__(self, key):
        return self._resources[key]

    def __setitem__(self, key, value):
        self._resources[key] = value
        self._modified = True

    def __delitem__(self, key):
        del self._resources[key]
        self._modified = True

    def __len__(self):
        return len(self._resources)

    def insert(self, index, obj):
        if not isinstance(obj, CkanResource):
            raise TypeError("Attempting to insert invalid object")
        return self._resources.insert(index, obj)

    def is_modified(self):
        if self._modified:
            return True
        if any(r.is_modified() for r in self._resources):
            return True
        return False

    def _get_by(self, field, value):
        for res in self._resources:
            if getattr(res, field) == value:
                return res
        return None

    def get_by_id(self, value):
        """Returns a resource, by id, or None"""
        return self._get_by('id', value)

    def get_by_name(self, value):
        """Returns a resource, by name, or None"""
        return self._get_by('name', value)

    def get_by_url(self, value):
        """Returns a resource, by url, or None"""
        return self._get_by('url', value)

    def filter(self, cond):
        # self._resources[:] = [r for r in self._resources if cond(r)]
        ## This allows filter(None, ...) too..
        self._resources[:] = filter(cond, self._resources)

    def sort(self, *a, **kw):
        self._resources.sort(*a, **kw)


class CkanResource(CkanObject):
    def __init__(self):
        self._original = {
            'id': None,
            'core': {},
        }
        self._updates = {'core': {}}

    @classmethod
    def from_dict(cls, obj):
        new_obj = cls()
        if 'id' in obj:
            new_obj._original['id'] = obj['id']
        for field in RESOURCE_FIELDS['core']:
            if field in obj:
                value = obj[field]
                setattr(new_obj, field, value)
        return new_obj

    def to_dict(self):
        object_as_dict = {}
        object_as_dict['id'] = self.id
        for field in RESOURCE_FIELDS['core']:
            object_as_dict[field] = getattr(self, field)
        return object_as_dict

    def is_modified(self):
        if self._original['core'] != {}:
            return True
        return False

    def __getattr__(self, name):
        if name == 'id':
            return self._original['id']

        if name in RESOURCE_FIELDS['core']:
            if name in self._updates:
                return self._updates[name]
            return self._original.get(name)

        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in ['_original', '_updates']:
            self.__dict__[name] = value
            return

        if name == 'id':
            raise RuntimeError("Cannot alter value of a field used as a key!")

        if name in RESOURCE_FIELDS['core']:
            if not isinstance(value, basestring):
                raise TypeError("Core fields must be strings")
            self._updates[name] = value
            return

        raise AttributeError(name)

    def __delattr__(self, name):
        raise RuntimeError("Cannot delete attribute")
