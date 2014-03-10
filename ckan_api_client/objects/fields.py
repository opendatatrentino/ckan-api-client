import copy

from .base import BaseField


__all__ = ['StringField', 'ListField', 'DictField',
           'GroupsField', 'ExtrasField']


class StringField(BaseField):
    default = ''

    def validate(self, instance, name, value):
        super(StringField, self).validate(instance, name, value)
        if not isinstance(value, basestring):
            raise TypeError("String field {0} value must be a string. "
                            "Got {1!r} instead.".format(name, type(value)))
        return value

    def serialize(self, instance, name):
        return self.get(instance, name)


class MutableFieldMixin(object):
    def get(self, instance, name):
        """
        When getting a mutable object, we need to make a copy,
        in order to make sure we are still able to detect changes.
        """

        if name not in instance._updates:
            if name in instance._values:
                value = instance._values[name]
            else:
                value = self.get_default()

            ## to be extra safe, make copy here, even on
            ## default values, which might get shared..
            instance._updates[name] = copy.deepcopy(value)

        return instance._updates[name]

    def serialize(self, instance, name):
        ## Copy to prevent unwanted mutation
        return copy.deepcopy(self.get(instance, name))

    def is_modified(self, instance, name):
        if name not in instance._updates:
            return False

        ## Otherwise, compare values to check whether
        ## field has been modified.

        if name in instance._values:
            default = instance._values[name]
        else:
            default = self.get_default()
        return default != instance._updates[name]


class ListField(MutableFieldMixin, BaseField):
    default = staticmethod(lambda: [])

    def validate(self, instance, name, value):
        value = super(ListField, self).validate(instance, name, value)
        if not isinstance(value, list):
            raise ValueError("{0} must be a list".format(name))
        return value


class DictField(MutableFieldMixin, BaseField):
    default = staticmethod(lambda: {})

    def validate(self, instance, name, value):
        value = super(DictField, self).validate(instance, name, value)
        if not isinstance(value, dict):
            raise ValueError("{0} must be a dict".format(name))
        return value


class GroupsField(ListField):
    def validate(self, instance, name, value):
        value = super(GroupsField, self).validate(instance, name, value)
        if not all(isinstance(x, basestring) for x in value):
            raise ValueError("{0} must be a list of strings".format(name))
        return value


class ExtrasField(DictField):
    def validate(self, instance, name, value):
        return super(ExtrasField, self).validate(instance, name, value)
