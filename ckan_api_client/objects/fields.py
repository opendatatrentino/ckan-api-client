import copy

from .base import BaseField


__all__ = ['StringField', 'ListField', 'DictField',
           'GroupsField', 'ExtrasField']


class StringField(BaseField):
    def validate(self, instance, name, value):
        super(StringField, self).validate(instance, name, value)
        if not isinstance(value, basestring):
            raise ValueError("{0} must be a string".format(name))

    def serialize(self, instance, name):
        return self.get(instance, name)


class MutableFieldMixin(object):
    def get(self, instance, name):
        """
        When getting a mutable object, we need to make a copy,
        in order to make sure we are still able to detect changes.
        """

        if name in instance._updates:
            return instance._updates[name]

        if name not in instance._values:
            instance._values[name] = self.get_default()
        instance._updates[name] = copy.deepcopy(instance._values[name])

        return instance._updates[name]

    def serialize(self, instance, name):
        ## Copy to prevent unwanted mutation
        return copy.deepcopy(self.get(instance, name))


class ListField(MutableFieldMixin, BaseField):
    default = staticmethod(lambda: [])

    def validate(self, instance, name, value):
        super(ListField, self).validate(instance, name, value)
        if not isinstance(value, list):
            raise ValueError("{0} must be a list".format(name))


class DictField(MutableFieldMixin, BaseField):
    default = staticmethod(lambda: {})

    def validate(self, instance, name, value):
        super(DictField, self).validate(instance, name, value)
        if not isinstance(value, dict):
            raise ValueError("{0} must be a dict".format(name))


class GroupsField(ListField):
    def validate(self, instance, name, value):
        super(GroupsField, self).validate(instance, name, value)
        if not all(isinstance(x, basestring) for x in value):
            raise ValueError("{0} must be a list of strings".format(name))


class ExtrasField(DictField):
    def validate(self, instance, name, value):
        super(Exception, self).validate(instance, name, value)
