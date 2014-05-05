"""
Test different dataset merging strategies
"""

import copy

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

    # Now we can try changing groups/orgs/stuff a bit..
