import pytest

from ckan_api_client.utils import freeze, FrozenDict, FrozenList


def test_frozendict():
    my_dict = {
        'key': 'DEFAULT',
    }

    my_frozen_dict = freeze(my_dict)
    assert my_dict == my_frozen_dict
    assert isinstance(my_frozen_dict, FrozenDict)

    # ----------------------------------------
    # We can mutate my_dict

    my_dict['key'] = 'UPDATED-1'
    assert my_dict['key'] == 'UPDATED-1'
    assert my_frozen_dict['key'] == 'DEFAULT'

    del my_dict['key']
    assert 'key' not in my_dict
    assert 'key' in my_frozen_dict
    assert my_frozen_dict['key'] == 'DEFAULT'

    my_dict['key'] = 'UPDATED-2'
    assert my_dict['key'] == 'UPDATED-2'
    assert my_frozen_dict['key'] == 'DEFAULT'

    # ----------------------------------------
    # We cannot mutate my_frozen_dict

    with pytest.raises(TypeError):
        my_frozen_dict['key'] = 'WROLD!!'

    with pytest.raises(TypeError):
        del my_frozen_dict['key']

    with pytest.raises(TypeError):
        my_frozen_dict.pop('key')

    with pytest.raises(TypeError):
        my_frozen_dict.update({'foo': 'bar'})

    assert my_dict['key'] == 'UPDATED-2'
    assert my_frozen_dict['key'] == 'DEFAULT'  # lowercase


def test_frozenlist():
    my_list = ['egg', 'spam']
    my_frozen_list = freeze(my_list)

    assert my_list == list(my_frozen_list)

    my_list.append('bacon')
    assert my_list == ['egg', 'spam', 'bacon']
    assert list(my_frozen_list) == ['egg', 'spam', 'bacon']

    with pytest.raises(TypeError):
        my_frozen_list[1] = 'SPAM!!'

    with pytest.raises(AttributeError):
        my_frozen_list.pop(0)

    with pytest.raises(AttributeError):
        my_frozen_list.extend(['spam'] * 10)


def test_frozen_nested():
    frozobj = freeze({
        'a list': [1, 2, 'a', 'b'],
        'a dict': {
            'key1': 'val1',
            'key2': 'val2',
        },
        'another list': [
            {'name': 'eggs', 'price': 1},
            {'name': 'spam', 'price': 2},
            {'name': 'bacon', 'price': 3},
        ]
    })

    assert isinstance(frozobj, FrozenDict)
    assert isinstance(frozobj['a list'], FrozenList)
