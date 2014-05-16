"""Tests for CkanDataset"""

import json
import itertools

import pytest

from ckan_api_client.objects import CkanDataset, CkanResource
from ckan_api_client.objects.ckan_dataset import ResourcesList
from ckan_api_client.utils import OrderedDict


def test_ckandataset_creation():
    dataset = CkanDataset({
        'name': 'example-dataset',
        'title': 'Example Dataset',
        'author': 'Foo Bar',
        'author_email': 'foobar@example.com',
        'extras': {'foo': 'bar', 'baz': 'SPAM!'},
        'groups': ['one', 'two', 'three'],
    })
    assert dataset.name == 'example-dataset'
    assert dataset.title == 'Example Dataset'
    assert dataset.groups == set(['one', 'two', 'three'])
    assert dataset.extras == {'foo': 'bar', 'baz': 'SPAM!'}

    assert isinstance(dataset.resources, ResourcesList)
    assert len(dataset.resources) == 0

    # The order of groups doesn't matter..
    _serialized = dataset.serialize()
    assert sorted(_serialized.pop('groups')) == sorted(['one', 'two', 'three'])

    assert _serialized == {
        'id': None,
        'name': 'example-dataset',
        'title': 'Example Dataset',
        'author': 'Foo Bar',
        'author_email': 'foobar@example.com',
        'license_id': '',
        'maintainer': '',
        'maintainer_email': '',
        'notes': '',
        'owner_org': '',
        'private': False,
        'state': 'active',
        'type': 'dataset',
        'url': '',
        'extras': {'foo': 'bar', 'baz': 'SPAM!'},
        'resources': [],
        'tags': [],
    }


def test_ckan_dataset_resources():
    dataset = CkanDataset({
        'name': 'example-dataset',
    })
    assert dataset.is_modified() is False

    # By asking for resources, a copy will be made,
    # but the two items should match..
    assert isinstance(dataset.resources, ResourcesList)
    assert len(dataset.resources) == 0
    assert dataset.is_modified() is False

    # Resources can be passed as normal objects and
    # will be converted to CkanResource() objects.
    dataset.resources = [
        {'name': 'resource-1'},
        {'name': 'resource-2'},
    ]

    # Make sure type conversions have been applied
    assert isinstance(dataset.resources, ResourcesList)
    for item in dataset.resources:
        assert isinstance(item, CkanResource)

    # Make sure dataset is marked as modified
    assert dataset.is_modified() is True

    # We allow comparison to plain objects
    assert dataset.resources == [
        {'name': 'resource-1'},
        {'name': 'resource-2'},
    ]

    # Or to the actual types used internally, of course
    assert dataset.resources == ResourcesList([
        CkanResource({'name': 'resource-1'}),
        CkanResource({'name': 'resource-2'}),
    ])

    # Do some tests for object serialization
    serialized = dataset.serialize()

    assert isinstance(serialized['resources'], list)
    assert len(serialized['resources']) == 2

    assert isinstance(serialized['resources'][0], dict)
    assert serialized['resources'][0]['name'] == 'resource-1'

    assert isinstance(serialized['resources'][1], dict)
    assert serialized['resources'][1]['name'] == 'resource-2'

    # Serialized data must be json-serializable
    json.dumps(serialized)


def test_ckandataset_resources_update():
    def _typecheck_resources(resources):
        assert isinstance(resources, ResourcesList)
        for item in resources:
            assert isinstance(item, CkanResource)

    dataset = CkanDataset({
        'name': 'example-dataset',
        'resources': [
            {'name': 'resource-1'},
            {'name': 'resource-2'},
        ]
    })
    assert dataset.is_modified() is False
    assert dataset.resources == [
        {'name': 'resource-1'},
        {'name': 'resource-2'},
    ]

    # Getting should not affect is_modified(), although
    # it is manipulating things internally..
    assert dataset.is_modified() is False

    dataset.resources.append({'name': 'resource-3'})
    assert dataset.is_modified() is True
    assert dataset.resources == [
        {'name': 'resource-1'},
        {'name': 'resource-2'},
        {'name': 'resource-3'},
    ]
    _typecheck_resources(dataset.resources)

    dataset.resources.insert(0, {'name': 'resource-0'})
    assert dataset.is_modified() is True
    assert dataset.resources == [
        {'name': 'resource-0'},
        {'name': 'resource-1'},
        {'name': 'resource-2'},
        {'name': 'resource-3'},
    ]
    _typecheck_resources(dataset.resources)

    dataset.resources[2] = {'name': 'RESOURCE-2'}
    assert dataset.is_modified() is True
    assert dataset.resources == [
        {'name': 'resource-0'},
        {'name': 'resource-1'},
        {'name': 'RESOURCE-2'},
        {'name': 'resource-3'},
    ]
    _typecheck_resources(dataset.resources)

    dataset.resources = [{'name': 'Hello'}]
    assert dataset.is_modified() is True
    assert dataset.resources == [
        {'name': 'Hello'},
    ]
    _typecheck_resources(dataset.resources)

    # "Contains" test is successful as fields left to
    # default values just get ignored during comparison.
    assert {'name': 'Hello'} in dataset.resources
    # assert {'name': 'WTF'} not in dataset.resources
    assert {'name': 'WTF, seriously'} not in dataset.resources


def test_resources_list():
    def _typecheck_resources(resources):
        assert isinstance(resources, ResourcesList)
        for item in resources:
            assert isinstance(item, CkanResource)

    rl1 = ResourcesList([
        CkanResource({'name': 'hello-resource'}),
    ])
    _typecheck_resources(rl1)

    rl2 = ResourcesList([
        {'name': 'hello-resource'},
    ])
    _typecheck_resources(rl2)

    rl3 = ResourcesList()
    rl3.append(CkanResource({'name': 'hello-resource'}))
    _typecheck_resources(rl3)

    rl4 = ResourcesList()
    rl4.append({'name': 'hello-resource'})
    _typecheck_resources(rl4)


# ------------------------------------------------------------
# Create datasets in different ways, compare them
# ------------------------------------------------------------


def _gen_ckandataset_update_extras_cases():
    def init_extras():
        return CkanDataset({'extras': {'KEY': 'VALUE'}})

    def set_extras():
        ds = CkanDataset()
        ds.extras['KEY'] = 'VALUE'
        return ds

    def upd_extras():
        ds = CkanDataset({'extras': {'KEY': 'ORIGINAL-VALUE'}})
        ds.extras['KEY'] = 'VALUE'
        return ds

    def add_extras():
        ds = CkanDataset()
        ds.extras = {'KEY': 'VALUE'}
        return ds

    def repl_extras():
        ds = CkanDataset({'extras': {'KEY': 'ORIGINAL-VALUE'}})
        ds.extras = {'KEY': 'VALUE'}
        return ds

    # We need to generate pairs
    functions = [(f.func_name, f) for f in [
        init_extras, set_extras, upd_extras, add_extras, repl_extras]]

    prod = itertools.product(functions, functions)
    return OrderedDict(
        (','.join((r[0][0], r[1][0])), (r[0][1], r[1][1]))
        for r in prod)


_ckandataset_update_extras_cases = \
    _gen_ckandataset_update_extras_cases()


@pytest.mark.parametrize('case_name', _ckandataset_update_extras_cases)
def test_ckandataset_update_extras(case_name):
    df1, df2 = _ckandataset_update_extras_cases[case_name]
    dataset1 = df1()
    dataset2 = df2()

    assert dataset1.is_equivalent(dataset2)
    assert dataset2.is_equivalent(dataset1)
    assert dataset1.serialize() == dataset2.serialize()
