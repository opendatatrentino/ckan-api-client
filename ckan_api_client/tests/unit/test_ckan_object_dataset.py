"""Tests for CkanDataset"""

import json

import pytest

from ckan_api_client.objects import CkanDataset, CkanResource
from ckan_api_client.objects.ckan_dataset import ResourcesList


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
    assert dataset.groups == ['one', 'two', 'three']
    assert dataset.extras == {'foo': 'bar', 'baz': 'SPAM!'}

    assert isinstance(dataset.resources, ResourcesList)
    assert len(dataset.resources) == 0

    assert dataset.serialize() == {
        'id': None,
        'name': 'example-dataset',
        'title': 'Example Dataset',
        'author': 'Foo Bar',
        'author_email': 'foobar@example.com',
        'license_id': None,
        'maintainer': None,
        'maintainer_email': None,
        'notes': None,
        'owner_org': None,
        'private': False,
        'state': 'active',
        'type': 'dataset',
        'url': None,
        'extras': {'foo': 'bar', 'baz': 'SPAM!'},
        'groups': ['one', 'two', 'three'],
        'resources': [],
    }


def test_ckan_dataset_resources():
    dataset = CkanDataset({
        'name': 'example-dataset',
    })
    assert dataset.is_modified() is False

    ## By asking for resources, a copy will be made,
    ## but the two items should match..
    assert isinstance(dataset.resources, ResourcesList)
    assert len(dataset.resources) == 0
    assert dataset.is_modified() is False

    ## Resources can be passed as normal objects and
    ## will be converted to CkanResource() objects.
    dataset.resources = [
        {'name': 'resource-1'},
        {'name': 'resource-2'},
    ]

    ## Make sure type conversions have been applied
    assert isinstance(dataset.resources, ResourcesList)
    for item in dataset.resources:
        assert isinstance(item, CkanResource)

    ## Make sure dataset is marked as modified
    assert dataset.is_modified() is True

    ## We allow comparison to plain objects
    assert dataset.resources == [
        {'name': 'resource-1'},
        {'name': 'resource-2'},
    ]

    ## Or to the actual types used internally, of course
    assert dataset.resources == ResourcesList([
        CkanResource({'name': 'resource-1'}),
        CkanResource({'name': 'resource-2'}),
    ])

    ## Do some tests for object serialization
    serialized = dataset.serialize()

    assert isinstance(serialized['resources'], list)
    assert len(serialized['resources']) == 2

    assert isinstance(serialized['resources'][0], dict)
    assert serialized['resources'][0]['name'] == 'resource-1'

    assert isinstance(serialized['resources'][1], dict)
    assert serialized['resources'][1]['name'] == 'resource-2'

    ## Serialized data must be json-serializable
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

    ## Getting should not affect is_modified(), although
    ## it is manipulating things internally..
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

    ## "Contains" test is successful as fields left to
    ## default values just get ignored during comparison.
    assert {'name': 'Hello'} in dataset.resources
    assert {'name': 'WTF'} not in dataset.resources


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
