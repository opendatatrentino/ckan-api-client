"""Tests for the base model objects"""

import pytest

from ckan_api_client.objects import (
    BaseObject, BaseField, StringField, ListField, DictField)


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

    ## try changing first object
    obj1.spam = 10
    obj1.eggs = 20
    with pytest.raises(AttributeError):
        obj1.doesnotexist = 10
    assert obj1.spam == 10
    assert obj1.eggs == 20

    ## Other object should be unaffected
    assert obj2.spam == 100
    assert obj2.bacon == 50

    ## restore original values
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
    assert obj.to_dict() == {'fld1': 'hello', 'fld2': 'Hi!', 'fld3': None}


def test_complex_fields():
    class MyObject(BaseObject):
        fld1 = StringField()
        fld2 = ListField()
        fld3 = DictField()
    obj = MyObject({
        'fld1': 'hello',
        'fld2': ['1', '2', '3'],
        'fld3': {'a': 'A', 'b': 'B'},
    })

    assert obj.fld1 == 'hello'
    assert obj.fld2 == ['1', '2', '3']
    assert obj.fld3 == {'a': 'A', 'b': 'B'}

    assert obj.serialize() == {
        'fld1': 'hello',
        'fld2': ['1', '2', '3'],
        'fld3': {'a': 'A', 'b': 'B'},
    }
