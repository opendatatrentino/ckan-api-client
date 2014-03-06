import pytest

from ckan_api_client.utils import freeze, FrozenDict, FrozenList


def test_frozendict():
    my_dict = {
        'hello': 'world',
        'eggs': 'bacon',
    }
    my_frozen_dict = freeze(my_dict)
    assert my_dict == my_frozen_dict

    my_dict['hello'] = 'World'
    del my_dict['hello']
    my_dict['hello'] = 'World'  # restore..

    assert my_dict['hello'] == 'World'
    assert my_frozen_dict['hello'] == 'World'

    with pytest.raises(TypeError):
        my_frozen_dict['hello'] = 'WROLD!!'

    with pytest.raises(TypeError):
        del my_frozen_dict['hello']

    with pytest.raises(AttributeError):
        ## frozen dict doesn't have pop()
        my_frozen_dict.pop('hello')

    assert my_dict['hello'] == 'World'
    assert my_frozen_dict['hello'] == 'World'


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
