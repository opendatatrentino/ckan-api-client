from .base import BaseObject
from .fields import StringField, GroupsField, ExtrasField, ListField, BoolField


__all__ = ['CkanGroup']


class CkanGroup(BaseObject):
    id = StringField(is_key=True)

    name = StringField()
    title = StringField(default='')
    approval_status = StringField(default='approved')
    description = StringField(default='')
    # image_display_url = StringField()
    image_url = StringField(default='')
    is_organization = BoolField(default=False)
    state = StringField(default='active')
    type = StringField(default='group')

    # Special fields
    extras = ExtrasField()
    groups = GroupsField()
    tags = ListField()
    # users = ListField()
