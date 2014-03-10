import pytest

from ckan_api_client.objects.base import BaseObject
from ckan_api_client.objects.fields import StringField, ListField, DictField
from ckan_api_client.objects.ckan_dataset import ResourcesList, ResourcesField


def test_string_field():
    ##--------------------------------------------------
    ## Field without default value

    class MyObject(BaseObject):
        field = StringField()

    ## --- Test #1: no initial values
    obj = MyObject()
    assert obj.field == ''
    assert obj.is_modified() is False

    ## --- Test #2: initial values
    obj = MyObject({'field': 'initial_value'})
    assert obj.field == 'initial_value'
    assert obj.is_modified() is False

    ## --- Test #3: empty initial values
    obj = MyObject({})
    assert obj.field == ''
    assert obj.is_modified() is False

    ##--------------------------------------------------
    ## Field with default value

    class MyObject2(BaseObject):
        field = StringField(default='default_value')

    ## --- Test #1: no initial values
    obj = MyObject2()

    ## Make sure default value is used correctly
    assert obj.field == 'default_value'
    assert obj.is_modified() is False

    ## Try updating field
    obj.field = 'updated_value'
    assert obj.is_modified() is True
    assert obj.field == 'updated_value'

    ## Deleting the field will restore initial value
    del obj.field
    assert obj.is_modified() is False

    ## --- Test #2: initial values
    obj = MyObject2({'field': 'initial_value'})

    ## Make sure initial value is used instead of default
    assert obj.field == 'initial_value'
    assert obj.is_modified() is False

    ## Try updating field
    obj.field = 'updated_value'
    assert obj.is_modified() is True
    assert obj.field == 'updated_value'

    ## Deleting the field will restore initial value
    del obj.field
    assert obj.is_modified() is False

    ## --- Test #3: empty initial values
    obj = MyObject2({})

    assert obj.field == 'default_value'
    assert obj.is_modified() is False


def test_string_field_invalid_values():
    class MyObject1(BaseObject):
        field = StringField()

    class MyObject2(BaseObject):
        field = StringField(default='default_value')

    obj1 = MyObject1()
    assert obj1.field == ''
    with pytest.raises(TypeError):
        obj1.field = None
    with pytest.raises(TypeError):
        obj1.field = 123
    del obj1

    obj1 = MyObject1({'field': 'initial_value'})
    assert obj1.field == 'initial_value'
    with pytest.raises(TypeError):
        obj1.field = None
    with pytest.raises(TypeError):
        obj1.field = 123
    del obj1

    obj2 = MyObject2()
    assert obj2.field == 'default_value'
    with pytest.raises(TypeError):
        obj2.field = None
    with pytest.raises(TypeError):
        obj2.field = 123
    del obj2

    obj2 = MyObject2({'field': 'initial_value'})
    assert obj2.field == 'initial_value'
    with pytest.raises(TypeError):
        obj2.field = None
    with pytest.raises(TypeError):
        obj2.field = 123
    del obj2


def test_string_field_serialize():
    class MyObject1(BaseObject):
        field = StringField()

    class MyObject2(BaseObject):
        field = StringField(default='default_value')

    obj = MyObject1()
    assert obj.serialize() == {'field': ''}
    obj.field = 'updated_value'
    assert obj.serialize() == {'field': 'updated_value'}
    del obj

    obj = MyObject1({'field': 'initial_value'})
    assert obj.serialize() == {'field': 'initial_value'}
    obj.field = 'updated_value'
    assert obj.serialize() == {'field': 'updated_value'}
    del obj

    obj = MyObject2()
    assert obj.serialize() == {'field': 'default_value'}
    obj.field = 'updated_value'
    assert obj.serialize() == {'field': 'updated_value'}
    del obj

    obj = MyObject2({'field': 'initial_value'})
    assert obj.serialize() == {'field': 'initial_value'}
    obj.field = 'updated_value'
    assert obj.serialize() == {'field': 'updated_value'}
    del obj


def test_string_fiel_multiple():
    """
    We need to make sure multiple fields are not affecting
    each other, i.e. they don't keep unwanted state.
    """

    class MyObject(BaseObject):
        field1 = StringField()
        field2 = StringField()
        field3 = StringField(default='F3-default')
        field4 = StringField(default='F4-default')

    obj1 = MyObject()
    obj2 = MyObject()
    obj3 = MyObject({'field1': 'F1-initial', 'field3': 'F3-initial'})
    obj4 = MyObject({'field2': 'F2-initial', 'field4': 'F4-initial'})

    ##----------------------------------------
    ## Initial checks

    assert obj1.serialize() == {
        'field1': '',
        'field2': '',
        'field3': 'F3-default',
        'field4': 'F4-default',
    }
    assert obj2.serialize() == {
        'field1': '',
        'field2': '',
        'field3': 'F3-default',
        'field4': 'F4-default',
    }
    assert obj3.serialize() == {
        'field1': 'F1-initial',
        'field2': '',
        'field3': 'F3-initial',
        'field4': 'F4-default',
    }
    assert obj4.serialize() == {
        'field1': '',
        'field2': 'F2-initial',
        'field3': 'F3-default',
        'field4': 'F4-initial',
    }

    ##----------------------------------------
    ## Perform updates and run other checks

    obj1.field1 = 'F1-updated'
    obj1.field2 = 'F2-updated'
    obj1.field3 = 'F3-updated'
    obj1.field4 = 'F4-updated'

    assert obj1.serialize() == {
        'field1': 'F1-updated',
        'field2': 'F2-updated',
        'field3': 'F3-updated',
        'field4': 'F4-updated',
    }
    assert obj2.serialize() == {
        'field1': '',
        'field2': '',
        'field3': 'F3-default',
        'field4': 'F4-default',
    }
    assert obj3.serialize() == {
        'field1': 'F1-initial',
        'field2': '',
        'field3': 'F3-initial',
        'field4': 'F4-default',
    }
    assert obj4.serialize() == {
        'field1': '',
        'field2': 'F2-initial',
        'field3': 'F3-default',
        'field4': 'F4-initial',
    }

    ##--------------------------------------------------
    ## Restore values

    del obj1.field1
    del obj1.field2
    del obj1.field3
    del obj1.field4

    assert obj1.serialize() == {
        'field1': '',
        'field2': '',
        'field3': 'F3-default',
        'field4': 'F4-default',
    }


def test_list_field():
    class MyObject(BaseObject):
        field1 = ListField()
        field2 = ListField(default=lambda: [1, 2, 3])
    pass
