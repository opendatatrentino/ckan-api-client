"""
Classes to represent / validate Ckan objects.
"""

import warnings
import collections

__all__ = ['BaseField', 'BaseObject']


NOTSET = object()
MAPPING_TYPES = (dict, collections.Mapping)
SEQUENCE_TYPES = (list, tuple, collections.Sequence)


class BaseField(object):
    """
    Pseudo-descriptor, accepting field names along with instance,
    to allow better retrieving data for the instance itself.

    .. warning::
        Beware that fields shouldn't carry state of their own, a part
        from the one used for generic field configuration, as they
        are shared between instances.
    """

    default = None
    is_key = False

    def __init__(self, default=NOTSET, is_key=NOTSET, required=False):
        """
        :param default:
            Default value (if not callable) or function
            returning default value (if callable).
        :param is_key:
            Boolean indicating whether this is a key field
            or not. Key fields are ignored when comparing
            using :py:meth:`is_equivalent`
        """

        # todo: refactor to use kwargs

        if default is not NOTSET:
            self.default = default
        if is_key is not NOTSET:
            self.is_key = is_key
        self.required = required

        self._conf = {
            'default': self.default,
            'is_key': self.is_key,
            'required': self.required,
        }

    def get(self, instance, name):
        """
        Get the value for the field from the main instace,
        by looking at the first found in:

        - the updated value
        - the initial value
        - the default value
        """

        if name in instance._updates:
            return instance._updates[name]

        if name in instance._values:
            return instance._values[name]

        return self.get_default()

    def get_default(self):
        if callable(self.default):
            return self.default()
        return self.default

    def validate(self, instance, name, value):
        """
        The validate method should be the (updated)
        value to be used as the field value, or raise
        an exception in case it is not acceptable at all.
        """
        return value

    def set_initial(self, instance, name, value):
        """Set the initial value for a field"""
        value = self.validate(instance, name, value)
        instance._values[name] = value

    def set(self, instance, name, value):
        """Set the modified value for a field"""
        value = self.validate(instance, name, value)
        instance._updates[name] = value

    def delete(self, instance, name):
        """
        Delete the modified value for a field (logically
        restores the original one)
        """
        # We don't want an exception here, as we just restore
        # field to its initial value..
        instance._updates.pop(name, None)

    def serialize(self, instance, name):
        """
        Returns the "serialized" (json-encodable) version of
        the object.
        """
        return self.get(instance, name)

    def is_modified(self, instance, name):
        """
        Check whether this field has been modified on the
        main instance.
        """
        return name in instance._updates

    def is_equivalent(self, instance, name, other, ignore_key=True):
        if ignore_key and self.is_key:

            # If we want to ignore keys from comparison,
            # key comparison should always return True
            # for fields marked as keys.

            # --------------------------------------------------
            # NOTE: This should not be needed, as this part
            # won't even be called in case it is a key **and**
            # ignore_key=True. Its main purpose is to be
            # used recursively by fields containing related
            # objects.
            # --------------------------------------------------

            return True

        # Just perform simple comparison between values
        myvalue = getattr(instance, name)
        othervalue = getattr(other, name)
        if myvalue is None:
            myvalue = self.get_default()
        if othervalue is None:
            othervalue = self.get_default()
        return myvalue == othervalue

    def __repr__(self):
        myname = self.__class__.__name__
        kwargs = ', '.join('{0}={1!r}'.format(key, value)
                           for key, value in self._conf.iteritems())
        return "{0}({1})".format(myname, kwargs)


class BaseObject(object):
    """
    Base for the other objects, dispatching get/set/deletes
    to ``BaseField`` instances, if available.
    """

    _values = None
    _updates = None

    def __init__(self, values=None):
        if values is None:
            values = {}
        if not isinstance(values, MAPPING_TYPES):
            raise TypeError("Initial values must be a dict (or None). "
                            "Got {0!r} instead".format(type(values)))

        # Prepare variables to hold initial / updated values
        self._values = {}
        self._updates = {}

        # Set initial field values, by calling set_initial()
        # on the fields themselves.
        self.set_initial(values)

    @classmethod
    def from_dict(cls, data):
        warnings.warn("from_dict() is deprecated -- use normal constructor",
                      DeprecationWarning)
        return cls(data)

    def set_initial(self, values):
        """Set initial values for all fields"""
        for name, field in self.iter_fields():
            if name in values:
                field.set_initial(self, name, values[name])

    def to_dict(self):
        warnings.warn("to_dict() is deprecated -- use serialize()",
                      DeprecationWarning)
        return self.serialize()

    def __getattribute__(self, key):
        """
        Custom attribute handling.
        If the attribute is a field, return the value returned
        from its .get() method. Otherwise, return it directly.
        """
        attr = object.__getattribute__(self, key)
        if isinstance(attr, BaseField):
            return attr.get(self, key)
        return attr

    def __setattr__(self, key, value):
        """
        Custom attribute handling.
        If the attribute is a field, pass the value to its
        .set() method. Otherwise, set it directly on the object.
        """
        v = object.__getattribute__(self, key)
        if isinstance(v, BaseField):
            return v.set(self, key, value)
        return object.__setattr__(self, key, value)

    def __delattr__(self, key):
        """
        Custom attribute handling.
        If the attribute is a field, call its .del() method.
        Otherwise, perform the action directly on the object.
        """
        v = object.__getattribute__(self, key)
        if isinstance(v, BaseField):
            return v.delete(self, key)
        return object.__delattr__(self, key)

    def serialize(self):
        """
        Create a serializable representation of the object.
        """
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

    def is_equivalent(self, other, ignore_key=True):
        """
        Equivalency check between objects.
        Will make sure that values in all the non-key
        fields match.

        :param other:
            other object to compare
        :param ignore_key:
            if set to True (the default), it will ignore
            "key" fields during comparison
        """

        if type(self) != type(other):
            # We want to make sure the objects are of the
            # exact same type, not of some sub-type.
            return False

        for name, field in self.iter_fields():
            # Ignore key fields if we are required to
            # ignore keys.
            if ignore_key and field.is_key:
                continue

            # Use the equivalency check for fields
            if not field.is_equivalent(
                    self, name, other, ignore_key=ignore_key):
                return False

        return True

    def __eq__(self, other):
        return self.is_equivalent(other, ignore_key=False)

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_modified(self):
        """
        The object is modified if any of its fields reports
        itself as modified.
        """

        for name, field in self.iter_fields():
            if field.is_modified(self, name):
                return True
        return False

    def __repr__(self):
        return u'{0}({1})'.format(self.__class__.__name__, self.serialize())
