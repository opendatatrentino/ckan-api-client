"""Tests for the base model objects"""

import pytest

from ckan_api_client.objects import BaseObject, BaseField, StringField


def test_simple_baseobject():
    class MyObject(BaseObject):
        spam = BaseField()
        eggs = BaseField()
        bacon = BaseField()

    obj1 = MyObject({'spam': 1, 'eggs': 2})
    obj2 = MyObject({'spam': 100, 'bacon': 50})

    assert obj1.spam == 1
    assert obj1.eggs == 2
    assert obj1.bacon is None
    with pytest.raises(AttributeError):
        obj1.doesnotexist

    assert obj2.spam == 100
    assert obj2.bacon == 50
    assert obj2.eggs is None
    with pytest.raises(AttributeError):
        obj1.doesnotexist

    # try changing first object
    obj1.spam = 10
    obj1.eggs = 20
    with pytest.raises(AttributeError):
        obj1.doesnotexist = 10
    assert obj1.spam == 10
    assert obj1.eggs == 20

    # Other object should be unaffected
    assert obj2.spam == 100
    assert obj2.bacon == 50

    # restore original values
    del obj1.spam
    del obj1.eggs
    del obj1.bacon
    with pytest.raises(AttributeError):
        del obj1.doesnotexist
    assert obj1.spam == 1
    assert obj1.eggs == 2


def test_object_inspection():
    class MyObject(BaseObject):
        fld1 = StringField()
        fld2 = StringField()
    obj = MyObject()
    fields = list(obj.iter_fields())
    assert len(fields) == 2
    fields_dict = dict(fields)
    assert isinstance(fields_dict['fld1'], StringField)
    assert isinstance(fields_dict['fld2'], StringField)


def test_object_serialization():
    class MyObject(BaseObject):
        fld1 = StringField()
        fld2 = StringField(default=lambda: "Hi!")
        fld3 = StringField()

    obj = MyObject({'foo': 'ignored', 'fld1': 'hello'})
    assert obj.serialize() == {'fld1': 'hello', 'fld2': 'Hi!', 'fld3': None}


def test_object_comparison():
    class MyObject(BaseObject):
        field1 = StringField()
        field2 = StringField(default='something')
        field3 = StringField()

    obj1 = MyObject({'field1': 'value1'})
    obj2 = MyObject({'field1': 'value1'})
    assert obj1 == obj2
    assert obj1.is_equivalent(obj2)
    assert obj2.is_equivalent(obj1)

    obj1.field1 = 'another value'
    assert obj1 != obj2
    assert not obj1.is_equivalent(obj2)
    assert not obj2.is_equivalent(obj1)

    del obj1.field1
    assert obj1 == obj2
    assert obj1.is_equivalent(obj2)
    assert obj2.is_equivalent(obj1)


def test_object_comparison_type():
    class MyObject(BaseObject):
        pass

    class MySubObject1(MyObject):
        pass

    class MySubObject2(MyObject):
        pass

    assert not MyObject().is_equivalent({})
    assert not MyObject().is_equivalent('hello')
    assert not MyObject().is_equivalent(MySubObject1())
    assert not MySubObject1().is_equivalent(MyObject())
    assert not MySubObject1().is_equivalent(MySubObject2())


def test_object_comparison_with_key_field():
    # Now with "key" fields
    class MyObject2(BaseObject):
        id = StringField(is_key=True)
        field1 = StringField()
        field2 = StringField()

    obj1 = MyObject2({'id': 'eggs'})
    obj2 = MyObject2({'id': 'bacon'})
    assert obj1 != obj2
    assert obj1.is_equivalent(obj2)
    assert obj2.is_equivalent(obj1)

    obj1.field1 = 'spam'
    assert obj1 != obj2
    assert not obj1.is_equivalent(obj2)
    assert not obj2.is_equivalent(obj1)

    obj2.field1 = 'spam'
    assert obj1 != obj2
    assert obj1.is_equivalent(obj2)
    assert obj2.is_equivalent(obj1)


def test_object_comparison_with_default_vs_none():
    """
    Default value of a field should compare equal to ``None``
    for nullable fields.
    """

    class MyObject(BaseObject):
        field1 = StringField(default='')
        field2 = StringField(default='something')
        field3 = StringField(default='')

    obj1 = MyObject({'field1': 'val1', 'field2': None})
    obj2 = MyObject({'field1': 'val1', 'field3': ''})

    assert obj1.is_equivalent(obj2)


def test_object_invalid_init():
    class MyObject(BaseObject):
        field1 = StringField()
        field2 = StringField()

    with pytest.raises(TypeError):
        MyObject("this is not a dict")
    with pytest.raises(TypeError):
        MyObject(["this is", "not", "a dict"])


def test_object_depracation_warnings(recwarn):
    class MyObject(BaseObject):
        pass
    obj = MyObject()
    pytest.deprecated_call(obj.from_dict, {})
    pytest.deprecated_call(obj.to_dict)
