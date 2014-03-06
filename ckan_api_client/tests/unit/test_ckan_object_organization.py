"""Unit tests for CkanOrganization object"""

import copy

import pytest

from ckan_api_client.objects import CkanOrganization


@pytest.mark.xfail(run=False, reason='Work in progress')
def test_ckan_organization():
    raw_data = {
        # 'approval_status',
        # 'description',
        # 'image_display_url',
        # 'image_url',
        # 'is_organization',
        # 'name',
        # 'state',
        # 'title',
        # 'type',
    }

    ## Create an organization object.
    _raw_data = copy.deepcopy(raw_data)
    assert raw_data == _raw_data
    dataset = CkanDataset.from_dict(_raw_data)

    ## Make sure initial data hasn't been touched
    assert raw_data == _raw_data

    ## Make sure converting to dict returns the original dict.
    assert dataset.to_dict() == raw_data

    ## Try changing a key, make sure we got expected results
    dataset.author = 'My author'
    assert dataset.is_modified()
    assert dataset.to_dict()['author'] == 'My author'
    assert raw_data == _raw_data  # This is kept away

    ## Create a new dataset
    dataset = CkanDataset.from_dict(raw_data)
    assert not dataset.is_modified()
    del dataset.resources[2]  # delete 'resource-3'
    assert dataset.is_modified()
    dataset.resources.append(CkanResource.from_dict({
        'id': 'resource-4',
        'description': 'RES4-DESCRIPTION',
        'format': 'RES4-FORMAT',
        'mimetype': 'RES4-MIMETYPE',
        'mimetype_inner': 'RES4-MIMETYPE_INNER',
        'name': 'RES4-NAME',
        'position': 'RES4-POSITION',
        'resource_type': 'RES4-RESOURCE_TYPE',
        'size': 'RES4-SIZE',
        'url': 'RES4-URL',
        'url_type': 'RES4-URL_TYPE',
    }))
    assert dataset.to_dict()['resources'] == [
        {
            'id': 'resource-1',
            'description': 'RES1-DESCRIPTION',
            'format': 'RES1-FORMAT',
            'mimetype': 'RES1-MIMETYPE',
            'mimetype_inner': 'RES1-MIMETYPE_INNER',
            'name': 'RES1-NAME',
            'position': 'RES1-POSITION',
            'resource_type': 'RES1-RESOURCE_TYPE',
            'size': 'RES1-SIZE',
            'url': 'RES1-URL',
            'url_type': 'RES1-URL_TYPE',
        },
        {
            'id': 'resource-2',
            'description': 'RES2-DESCRIPTION',
            'format': 'RES2-FORMAT',
            'mimetype': 'RES2-MIMETYPE',
            'mimetype_inner': 'RES2-MIMETYPE_INNER',
            'name': 'RES2-NAME',
            'position': 'RES2-POSITION',
            'resource_type': 'RES2-RESOURCE_TYPE',
            'size': 'RES2-SIZE',
            'url': 'RES2-URL',
            'url_type': 'RES2-URL_TYPE',
        },
        {
            'id': 'resource-4',
            'description': 'RES4-DESCRIPTION',
            'format': 'RES4-FORMAT',
            'mimetype': 'RES4-MIMETYPE',
            'mimetype_inner': 'RES4-MIMETYPE_INNER',
            'name': 'RES4-NAME',
            'position': 'RES4-POSITION',
            'resource_type': 'RES4-RESOURCE_TYPE',
            'size': 'RES4-SIZE',
            'url': 'RES4-URL',
            'url_type': 'RES4-URL_TYPE',
        },
    ]
