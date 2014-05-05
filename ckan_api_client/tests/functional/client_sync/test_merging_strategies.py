"""
Test different dataset merging strategies
"""

import copy

import pytest

from ckan_api_client.exceptions import HTTPError
from ckan_api_client.high_level import CkanHighlevelClient
from ckan_api_client.syncing import SynchronizationClient


SAMPLE_DATA = {
    'dataset': {
        'dataset-1': {
            'name': 'dataset-1',
            'title': 'Dataset #1',
            'owner_org': 'org-1',
            'groups': ['grp-1'],
        },
        'dataset-2': {
            'name': 'dataset-2',
            'title': 'Dataset #2',
            'owner_org': 'org-1',
            'groups': ['grp-1', 'grp-2'],
        },
        'dataset-3': {
            'name': 'dataset-3',
            'title': 'Dataset #3',
            'owner_org': 'org-1',
            'groups': ['grp-2'],
        },
        'dataset-4': {
            'name': 'dataset-4',
            'title': 'Dataset #4',
            'owner_org': 'org-2',
            'groups': ['grp-3'],
        },
    },
    'group': {
        'grp-1': {'title': 'Group #1', 'name': 'grp-1'},
        'grp-2': {'title': 'Group #2', 'name': 'grp-2'},
        'grp-3': {'title': 'Group #3', 'name': 'grp-3'},
    },
    'organization': {
        'org-1': {'title': 'Organization #1', 'name': 'org-1'},
        'org-2': {'title': 'Organization #2', 'name': 'org-2'},
    },
}


def test_merge_strategies(ckan_client_arguments):
    args = ckan_client_arguments
    client = CkanHighlevelClient(*args[0], **args[1])
    sync_client = SynchronizationClient(*args[0], **args[1])
    data = copy.deepcopy(SAMPLE_DATA)

    # Sync data -- should create new datasets only
    sync_client.sync('test_merge', data)

    assert client.get_dataset_by_name('dataset-1').title == 'Dataset #1'
    assert client.get_organization_by_name('org-1').title == 'Organization #1'  # noqa
    assert client.get_group_by_name('grp-1').title == 'Group #1'  # noqa

    # Make sure we preserve names if told so
    # ------------------------------------------------------------

    sync_client._conf['dataset_preserve_names'] = True
    data['dataset']['dataset-1']['name'] = 'dummy-dataset-one'
    data['dataset']['dataset-1']['title'] = 'Dataset #1.1'
    sync_client.sync('test_merge', data)

    dataset = client.get_dataset_by_name('dataset-1')
    assert dataset.name == 'dataset-1'
    assert dataset.title == 'Dataset #1.1'

    # Make sure we update names if told so
    # ------------------------------------------------------------

    sync_client._conf['dataset_preserve_names'] = False
    data['dataset']['dataset-1']['name'] = 'dummy-dataset-one'
    data['dataset']['dataset-1']['title'] = 'Dataset #1.2'
    sync_client.sync('test_merge', data)

    with pytest.raises(HTTPError) as excinfo:
        # It got renamed!
        client.get_dataset_by_name('dataset-1')
    assert excinfo.value.status_code == 404

    # Get using the old id
    dataset = client.get_dataset(dataset.id)
    assert dataset.name == 'dummy-dataset-one'
    assert dataset.title == 'Dataset #1.2'

    # Get using the new name
    dataset = client.get_dataset_by_name('dummy-dataset-one')
    assert dataset.name == 'dummy-dataset-one'
    assert dataset.title == 'Dataset #1.2'

    # Prepare for merging groups
    # ============================================================

    grp1_id = client.get_group_by_name('grp-1').id
    grp2_id = client.get_group_by_name('grp-2').id
    # grp3_id = client.get_group_by_name('grp-3').id

    # Merge groups with 'replace' strategy
    # ------------------------------------------------------------

    dataset = client.get_dataset_by_name('dataset-2')
    assert dataset.groups == set([grp1_id, grp2_id])

    sync_client._conf['dataset_group_merge_strategy'] = 'replace'
    data['dataset']['dataset-2']['groups'] = ['grp-1']

    sync_client.sync('test_merge', data)
    dataset = client.get_dataset_by_name('dataset-2')
    assert dataset.groups == set([grp1_id])

    # Merge groups with 'add' strategy
    # ------------------------------------------------------------

    sync_client._conf['dataset_group_merge_strategy'] = 'add'
    data['dataset']['dataset-2']['groups'] = ['grp-2']

    sync_client.sync('test_merge', data)
    dataset = client.get_dataset_by_name('dataset-2')
    assert dataset.groups == set([grp1_id, grp2_id])

    # Merge groups with 'preserve' strategy
    # ------------------------------------------------------------

    sync_client._conf['dataset_group_merge_strategy'] = 'preserve'
    data['dataset']['dataset-2']['groups'] = ['grp-3']

    sync_client.sync('test_merge', data)
    dataset = client.get_dataset_by_name('dataset-2')
    assert dataset.groups == set([grp1_id, grp2_id])
