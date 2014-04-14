"""
Tests for group crud, using high-level client
"""

import pytest

from ckan_api_client.exceptions import HTTPError
from ckan_api_client.objects import CkanGroup
from ckan_api_client.tests.utils.generate import generate_group


def test_group_create(ckan_client_hl):
    client = ckan_client_hl
    obj_dict = generate_group()
    obj = CkanGroup(obj_dict)
    created = client.create_group(obj)
    assert created.is_equivalent(obj)


def test_group_get_by_name(ckan_client_hl):
    client = ckan_client_hl
    group_dict = generate_group()
    group_dict['name'] = 'example-group-name'
    group = CkanGroup(group_dict)
    created = client.create_group(group)
    assert created.is_equivalent(group)
    group_id = created.id

    # Try getting by id
    group_1 = client.get_group(group_id)
    assert created == group_1

    # Try getting by name
    group_2 = client.get_group_by_name(
        'example-group-name')
    assert created == group_2

    # Try getting by id, but passing name instead
    with pytest.raises(HTTPError) as excinfo:
        client.get_group('example-group-name')
    assert excinfo.value.status_code == 404

    # Try getting by name, but passing id instead
    with pytest.raises(HTTPError) as excinfo:
        client.get_group_by_name(group_id)
    assert excinfo.value.status_code == 404


def test_group_list(ckan_client_hl):
    client = ckan_client_hl

    # Create a bunch of groups
    obj_dicts = [generate_group() for _ in xrange(10)]
    objs = [CkanGroup(d) for d in obj_dicts]
    created_objs = [client.create_group(o) for o in objs]

    # Make sure all the orgnaizations are in the list
    obj_ids = client.list_groups()
    for obj in created_objs:
        assert obj.id is not None
        assert obj.id in obj_ids


def test_group_read(ckan_client_hl):
    client = ckan_client_hl

    obj_dict = generate_group()
    obj = CkanGroup(obj_dict)

    created = client.create_group(obj)
    assert obj.is_equivalent(created)
    assert created.is_equivalent(obj)
