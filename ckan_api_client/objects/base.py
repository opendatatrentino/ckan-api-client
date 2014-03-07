"""
Classes to represent / validate Ckan objects.
"""

import warnings


NOTSET = object()


class BaseField(object):
    """
    Pseudo-descriptor, accepting field names along with instance,
    to allow better retrieving data for the instance itself.
    """

    default = None

    def __init__(self, default=NOTSET):
        if default is not NOTSET:
            self.default = default

    def get(self, instance, name):
        if name in instance._updates:
            return instance._updates[name]
        if name not in instance._values:
            instance._values[name] = self.get_default()
        return instance._values[name]

    def get_default(self):
        if callable(self.default):
            return self.default()
        return self.default

    def validate(self, instance, name, value):
        pass

    def set(self, instance, name, value):
        self.validate(instance, name, value)
        instance._updates[name] = value

    def delete(self, instance, name):
        ## We don't want an exception here, as we just restore
        ## field to its initial value..
        instance._updates.pop(name, None)

    def serialize(self, instance, name):
        raise NotImplementedError


class BaseObject(object):
    """
    Base for the other objects, dispatching get/set/deletes
    to ``BaseField`` instances, if available.
    """

    _values = None
    _updates = None

    def __init__(self, values=None):
        if values is not None:
            if not isinstance(values, dict):
                values = dict(values.iteritems())
        else:
            values = {}
        self._values = values
        self._updates = {}

    @classmethod
    def from_dict(cls, data):
        warnings.warn("from_dict() is deprecated -- use normal constructor",
                      DeprecationWarning)
        return cls(data)

    def to_dict(self):
        warnings.warn("to_dict() is deprecated -- use serialize()",
                      DeprecationWarning)
        return self.serialize()

    def __getattribute__(self, key):
        v = object.__getattribute__(self, key)
        if isinstance(v, BaseField):
            return v.get(self, key)
        return v

    def __setattr__(self, key, value):
        v = object.__getattribute__(self, key)
        if isinstance(v, BaseField):
            return v.set(self, key, value)
        return object.__setattr__(self, key, value)

    def __delattr__(self, key):
        v = object.__getattribute__(self, key)
        if isinstance(v, BaseField):
            return v.delete(self, key)
        return object.__delattr__(self, key)

    def serialize(self):
        serialized = {}
        for name, field in self.iter_fields():
            serialized[name] = field.serialize(self, name)
        return serialized

    def iter_fields(self):
        """
        Iterate over fields in this objects, yielding
        (name, field) pairs.
        """
        for name in dir(self):
            attr = object.__getattribute__(self, name)
            if isinstance(attr, BaseField):
                yield name, attr
