from .base import BaseObject
from .fields import StringField, GroupsField, ExtrasField, ListField, BoolField


__all__ = ['CkanGroup']


class CkanGroup(BaseObject):
    id = StringField()

    name = StringField()
    title = StringField()
    approval_status = StringField()
    description = StringField()
    image_display_url = StringField()
    image_url = StringField()
    is_organization = BoolField(default=False)
    state = StringField(default='active')
    type = StringField(default='group')

    ## Special fields
    extras = ExtrasField()
    groups = GroupsField()
    tags = ListField()
    users = ListField()
