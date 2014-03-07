from .base import BaseObject
from .fields import StringField, GroupsField, ExtrasField, ListField


__all__ = ['ResourcesField', 'CkanDataset', 'CkanResource']


class ResourcesField(ListField):
    """
    The ResourcesField should behave pretty much as a list field,
    but will keep track of changes, and make sure all elements
    are CkanResources.
    """

    def get(self, instance, name):
        ## todo: replace value with appropriate object
        return super(ResourcesField, self).get(instance, name)


class CkanDataset(BaseObject):
    id = StringField()

    ## Core fields
    name = StringField()
    title = StringField()

    author = StringField()
    author_email = StringField()
    license_id = StringField()
    maintainer = StringField()
    maintainer_email = StringField()
    notes = StringField()
    owner_org = StringField()
    private = StringField(default=lambda: False)
    state = StringField(default=lambda: 'active')
    type = StringField(default=lambda: 'dataset')
    url = StringField()

    ## Special fields
    extras = ExtrasField()
    groups = GroupsField()
    resources = ResourcesField()
    # relationships = ListField()


class CkanResource(BaseObject):
    id = StringField()

    description = StringField()
    format = StringField()
    mimetype = StringField()
    mimetype_inner = StringField()
    name = StringField()
    position = StringField()
    resource_type = StringField()
    size = StringField()
    url = StringField()
    url_type = StringField()
