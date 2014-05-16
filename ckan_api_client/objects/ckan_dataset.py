from ckan_api_client.utils import WrappedList

from .base import BaseObject, MAPPING_TYPES
from .fields import (StringField, GroupsField, ExtrasField, ListField,
                     BoolField, SetField)


__all__ = ['ResourcesField', 'CkanDataset', 'CkanResource']


class ResourcesField(ListField):
    """
    The ResourcesField should behave pretty much as a list field,
    but will keep track of changes, and make sure all elements
    are CkanResources.
    """

    def validate(self, instance, name, value):
        if isinstance(value, ResourcesList):
            return value
        return ResourcesList(value)

    def serialize(self, instance, name):
        value = self.get(instance, name)
        assert isinstance(value, ResourcesList)
        return [
            r.serialize() for r in value
        ]

    def is_equivalent(self, instance, name, other, ignore_key=True):
        # We are now comparing two ResourcesList instances,
        # but we need to ignore all the key fields when comparing
        # resources

        our_value = getattr(instance, name)
        other_value = getattr(other, name)
        assert isinstance(our_value, ResourcesList)
        assert isinstance(other_value, ResourcesList)

        # Different length -- clearly two different things
        if len(our_value) != len(other_value):
            return False

        # Compare resources one-by-one, by calling their "is_equivalent"
        # methods.
        for resource1, resource2 in zip(our_value, other_value):
            if not resource1.is_equivalent(resource2, ignore_key=ignore_key):
                return False

        return True


class ResourcesList(WrappedList):
    def __init__(self, initial=None):
        if initial is None:
            super(ResourcesList, self).__init__()
        else:
            super(ResourcesList, self).__init__(
                self._check_item(item) for item in initial)

    def _check_item(self, value):
        if isinstance(value, MAPPING_TYPES):
            return CkanResource(value)
        if not isinstance(value, CkanResource):
            raise TypeError("Invalid resource. Must be a CkanResource "
                            "or a dict, got {0!r} instead."
                            .format(type(value)))
        return value

    def __setitem__(self, name, value):
        value = self._check_item(value)
        super(ResourcesList, self).__setitem__(name, value)

    def insert(self, pos, item):
        item = self._check_item(item)
        return super(ResourcesList, self).insert(pos, item)

    def __contains__(self, item):
        try:
            item = self._check_item(item)
        except TypeError:
            # Invalid type -- cannot be contained
            return False
        return super(ResourcesList, self).__contains__(item)


class CkanDataset(BaseObject):
    id = StringField(is_key=True)

    # Core fields
    name = StringField()
    title = StringField()

    author = StringField(default='')
    author_email = StringField(default='')
    license_id = StringField(default='')
    maintainer = StringField(default='')
    maintainer_email = StringField(default='')
    notes = StringField(default='')
    owner_org = StringField(default='')
    private = BoolField(default=False)
    state = StringField(default='active')
    type = StringField(default='dataset')
    url = StringField(default='')

    # Special fields
    extras = ExtrasField()
    groups = GroupsField()
    resources = ResourcesField()
    # relationships = ListField()
    tags = SetField()


class CkanResource(BaseObject):
    id = StringField(is_key=True)

    description = StringField(default='')
    format = StringField(default='')
    mimetype = StringField()
    mimetype_inner = StringField()
    name = StringField(default='')
    # position = IntegerField()  # Ignore, as it is generated
    resource_type = StringField(default='')
    size = StringField()
    url = StringField(default='')
    url_type = StringField()

    def __eq__(self, other):
        # To allow comparison with dict..
        # todo: move this in the BaseObject?
        if isinstance(other, MAPPING_TYPES):
            return self == CkanResource(other)
        return super(CkanResource, self).__eq__(other)
