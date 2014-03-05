import copy

import pytest

from ckan_api_client.schema import (DATASET_FIELDS, RESOURCE_FIELDS,
                                    GROUP_FIELDS)
from ckan_api_client.tests.utils.strings import gen_random_id


OUR_GROUPS = [
    {'name': 'group-01', 'title': 'Group 01'},
    {'name': 'group-02', 'title': 'Group 02'},
    {'name': 'group-03', 'title': 'Group 03'},
]
OUR_ORG = {
    'name': 'custom-organization',
    'title': 'Custom Organization',
}
OUR_DATASET = {
    "author": "Servizio Statistica",
    "author_email": "serv.statistica@provincia.tn.it",

    "extras": {
        "Aggiornamento": "Annuale",
        "Codifica Caratteri": "UTF-8",
        "Copertura Geografica": "Provincia di Trento",
        "Copertura Temporale (Data di inizio)": "1985-01-01T00:00:00",
        "Data di aggiornamento": "2012-01-01T00:00:00",
        "Data di pubblicazione": "2013-06-16T11:45:26.324274",
        "Titolare": "Provincia Autonoma di Trento"
    },

    "groups": [
        # todo: fill with ids of the previous groups
    ],

    "license_id": "cc-by",
    "maintainer": "Servizio Statistica",
    "maintainer_email": "serv.statistica@provincia.tn.it",
    "name": "presenza-media-in-alberghi-comparati-e-alloggi",
    "notes": "**Presenza media in alberghi, comparati e alloggi**",

    # todo: fill with if of the previous organization
    # "owner_org": "4c3d9698-2f8e-49fa-ab6b-7b572862e36d",

    "private": False,

    "resources": [
        {
            "description": "Presenza media in alberghi, comparati e alloggi",
            "format": "JSON",
            "hash": "",
            "mimetype": "text/html",
            "mimetype_inner": None,
            "name": "presenza-media-in-alberghi-comparati-e-alloggi",
            "position": 0,
            "resource_type": "api",
            "size": "279202",
            "url": "http://statistica.example.com/dataset-242.json",
            "url_type": None,
        },
        {
            "description": "Presenza media in alberghi, comparati e alloggi",
            "format": "CSV",
            "hash": "706d4e38e6c1d167e5e9ef1a3a8358a581bcf157",
            "mimetype": "text/csv",
            "mimetype_inner": None,
            "name": "presenza-media-in-alberghi-comparati-e-alloggi",
            "position": 1,
            "resource_type": "file",
            "size": "78398",
            "url": "http://statistica.example.com/dataset-242.csv",
            "url_type": None,
        },
        {
            "description": ("Media giornaliera di presenze in strutture "
                            "alberghiere, complementari e alloggi"),
            "format": "JSON",
            "hash": "",
            "mimetype": "application/json",
            "mimetype_inner": None,
            "name": ("media-giornaliera-di-presenze-in-strutture-alberghiere-"
                     "complementari-e-alloggi"),
            "position": 2,
            "resource_type": "api",
            "size": None,
            "url": "http://statistica.example.com/dataset-242-d.json",
            "url_type": None,
        },
        {
            "description": ("Media giornaliera di presenze in strutture "
                            "alberghiere, complementari e alloggi"),
            "format": "CSV",
            "hash": "9d05c7959b0fae4b13b00e81dd15a0bf9e3d707a",
            "mimetype": "text/csv",
            "mimetype_inner": None,
            "name": ("media-giornaliera-di-presenze-in-strutture-alberghiere-"
                     "complementari-e-alloggi"),
            "position": 3,
            "resource_type": "file",
            "size": "8332",
            "url": "http://statistica.example.com/dataset-242-d.csv",
            "url_type": None,
        }
    ],
    "state": "active",
    "tags": [
        "servizi",
        "settori economici"
    ],
    "title": "Presenza media in alberghi, comparati e alloggi",
    "type": "dataset",
    "url": "http://www.statistica.provincia.tn.it",
}


@pytest.fixture
def ckan_client(request, ckan_env):
    from ckan_api_client.low_level import CkanLowlevelClient

    api_key = ckan_env.get_sysadmin_api_key()
    server = ckan_env.serve()
    client = CkanLowlevelClient(server.url, api_key)

    def finalize():
        server.stop()
    request.addfinalizer(finalize)

    server.start()

    return client


def prepare_dataset(ckan_client, base=None):
    if base is None:
        base = OUR_DATASET
    our_dataset = copy.deepcopy(base)

    ## We need to change name, as it must be unique

    dataset_name = "dataset-{0}".format(gen_random_id())
    our_dataset['name'] = dataset_name
    our_dataset['title'] = "Test dataset {0}".format(dataset_name)

    ## Figure out the groups

    our_groups_ids = []

    # all_groups = list(ckan_client.iter_groups())
    # all_groups_by_name = dict((x['name'], x) for x in all_groups)

    for group in OUR_GROUPS:
        _group = ckan_client.upsert_group(group)
        our_groups_ids.append(_group['id'])

    our_dataset['groups'] = our_groups_ids

    ## Figure out the organization

    our_org_id = None

    all_orgs = list(ckan_client.iter_organizations())
    all_orgs_by_name = dict((x['name'], x) for x in all_orgs)

    if OUR_ORG['name'] in all_orgs_by_name:
        _org = all_orgs_by_name[OUR_ORG['name']]
    else:
        _org = ckan_client.post_organization(OUR_ORG)
    our_org_id = _org['id']

    our_dataset['owner_org'] = our_org_id

    return our_dataset


def get_dummy_dataset(ckan_client):
    return prepare_dataset(ckan_client)


def get_dummy_group(ckan_client):
    code = gen_random_id()
    return {
        "approval_status": "approved",
        "description": "Example group {0}".format(code),
        "display_name": "Group {0}".format(code),
        "extras": {
            'group_code': code,
        },
        "groups": [],  # ?? -> parent groups?
        "image_display_url": "http://example.com/pic.png",
        "image_url": "http://example.com/pic.png",
        "is_organization": False,
        "name": "group-{0}".format(code),
        # "packages": [],
        "state": "active",
        # "tags": [],
        "title": "Group {0}".format(code),
        "type": "group",
        # "users": [],
    }


def check_dataset(dataset, expected):
    """
    Check that a dataset matches the expected one.

    - check all core fields
    - check extras, if specified
    - check groups, if specified

    WARNING: This function uses asserts, only use in your test code!
    """

    for field in DATASET_FIELDS['core']:
        if field in expected:
            assert dataset[field] == expected[field]

    if 'extras' in expected:
        assert dataset['extras'] == expected['extras']

    if 'groups' in expected:
        assert sorted(dataset['groups']) == sorted(expected['groups'])

    ## Check resources
    if 'resources' in expected:
        _dataset_resources = dict((x['url'], x) for x in dataset['resources'])
        _expected_resources = dict((x['url'], x)
                                   for x in expected['resources'])

        assert len(_dataset_resources) == len(dataset['resources'])
        assert len(_expected_resources) == len(expected['resources'])
        assert len(_dataset_resources) == len(_expected_resources)

        assert sorted(_dataset_resources.iterkeys()) \
            == sorted(_expected_resources.iterkeys())

        for key in _dataset_resources:
            _resource = _dataset_resources[key]
            _expected = _expected_resources[key]
            for field in RESOURCE_FIELDS['core']:
                assert _resource[field] == _expected[field]


def check_group(group, expected):
    for field in GROUP_FIELDS['core']:
        if field in expected:
            assert group[field] == expected[field]

    if 'extras' in expected:
        assert group['extras'] == expected['extras']

    if 'groups' in expected:
        assert sorted(group['groups']) == sorted(expected['groups'])

    if 'tags' in expected:
        assert sorted(group['tags']) == sorted(expected['tags'])

    if 'users' in expected:
        assert sorted(x['id'] for x in group['users']) \
            == sorted(x['id'] for x in expected['users'])
