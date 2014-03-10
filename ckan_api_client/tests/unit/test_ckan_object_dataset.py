"""Tests for CkanDataset"""

from ckan_api_client.objects import CkanDataset, CkanResource


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
    assert dataset.resources == []

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


def test_ckandataset_resources():
    dataset = CkanDataset({
        'name': 'example-dataset',
    })
    assert dataset.is_modified() is False

    ## By asking for resources, a copy will be made,
    ## but the two items should match..
    assert dataset.resources == []
    assert dataset.is_modified() is False

    dataset.resources = [
        CkanResource({'name': 'resource-1'}),
        CkanResource({'name': 'resource-2'}),
    ]
    assert dataset.resources == [
        CkanResource({'name': 'resource-1'}),
        CkanResource({'name': 'resource-2'}),
    ]
    assert dataset.is_modified() is True

    serialized = dataset.serialize()
    assert isinstance(serialized['resources'], list)
    assert len(serialized['resources']) == 2
    assert isinstance(serialized['resources'][0], CkanResource)
    assert serialized['resources'][0].name == 'resource-1'
    assert isinstance(serialized['resources'][1], CkanResource)
    assert serialized['resources'][1].name == 'resource-2'
