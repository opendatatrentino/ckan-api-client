import copy

import pytest

from ckan_api_client.objects import CkanDataset, CkanResource


@pytest.mark.xfail(run=False, reason="Need work on new objects")
def test_ckan_dataset():
    raw_data = {
        'id': 'dataset-1',
        'author': 'DATASET-AUTHOR',
        'author_email': 'DATASET-AUTHOR_EMAIL',
        'license_id': 'DATASET-LICENSE_ID',
        'maintainer': 'DATASET-MAINTAINER',
        'maintainer_email': 'DATASET-MAINTAINER_EMAIL',
        'name': 'DATASET-NAME',
        'notes': 'DATASET-NOTES',
        'owner_org': 'DATASET-OWNER_ORG',
        'private': 'DATASET-PRIVATE',
        'state': 'DATASET-STATE',
        'type': 'DATASET-TYPE',
        'url': 'DATASET-URL',
        'extras': {
            'EXTRA_KEY_1': 'EXTRA-VALUE-1',
            'EXTRA_KEY_2': 'EXTRA-VALUE-2',
            'EXTRA_KEY_3': 'EXTRA-VALUE-3',
        },
        'groups': ['GROUP-1', 'GROUP-2', 'GROUP-3'],
        'relationships': [],
        'resources': [
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
                'id': 'resource-3',
                'description': 'RES3-DESCRIPTION',
                'format': 'RES3-FORMAT',
                'mimetype': 'RES3-MIMETYPE',
                'mimetype_inner': 'RES3-MIMETYPE_INNER',
                'name': 'RES3-NAME',
                'position': 'RES3-POSITION',
                'resource_type': 'RES3-RESOURCE_TYPE',
                'size': 'RES3-SIZE',
                'url': 'RES3-URL',
                'url_type': 'RES3-URL_TYPE',
            },
        ]
    }
    _raw_data = copy.deepcopy(raw_data)
    assert raw_data == _raw_data
    dataset = CkanDataset.from_dict(_raw_data)
    assert raw_data == _raw_data
    assert dataset.to_dict() == raw_data

    dataset.author = 'My author'
    assert dataset.is_modified()
    assert dataset.to_dict()['author'] == 'My author'

    # Create a new dataset
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
