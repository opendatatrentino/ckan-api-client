"""Tests for CkanDataset"""

from ckan_api_client.objects import CkanDataset


def test_ckandataset_creation():
    dataset = CkanDataset({
        'name': 'example-dataset',
        'title': 'Example Dataset',
        'author': 'Foo Bar',
        'author_email': 'foobar@example.com',
    })
    assert dataset.name == 'example-dataset'
    assert dataset.title == 'Example Dataset'
    assert dataset.groups == []
    assert dataset.extras == {}
    assert dataset.resources == []
