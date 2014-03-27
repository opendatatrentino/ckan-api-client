"""
Tests for organization crud, using high-level client.
"""

import pytest

from ckan_api_client.exceptions import HTTPError
from ckan_api_client.objects import CkanOrganization
from ckan_api_client.tests.utils.generate import generate_organization


def test_organization_create(ckan_client_hl):
    client = ckan_client_hl
    obj_dict = generate_organization()
    obj = CkanOrganization(obj_dict)
    created = client.create_organization(obj)
    assert created.is_equivalent(obj)


def test_organization_get_by_name(ckan_client_hl):
    client = ckan_client_hl
    organization_dict = generate_organization()
    organization_dict['name'] = 'example-organization-name'
    organization = CkanOrganization(organization_dict)
    created = client.create_organization(organization)
    assert created.is_equivalent(organization)
    organization_id = created.id

    # Try getting by id
    organization_1 = client.get_organization(organization_id)
    assert created == organization_1

    # Try getting by name
    organization_2 = client.get_organization_by_name(
        'example-organization-name')
    assert created == organization_2

    # Try getting by id, but passing name instead
    with pytest.raises(HTTPError) as excinfo:
        client.get_organization('example-organization-name')
    assert excinfo.value.status_code == 404

    # Try getting by name, but passing id instead
    with pytest.raises(HTTPError) as excinfo:
        client.get_organization_by_name(organization_id)
    assert excinfo.value.status_code == 404


def test_organization_list(ckan_client_hl):
    client = ckan_client_hl

    # Create a bunch of organizations
    obj_dicts = [generate_organization() for _ in xrange(10)]
    objs = [CkanOrganization.from_dict(d) for d in obj_dicts]
    created_objs = [client.create_organization(o) for o in objs]

    # Make sure all the orgnaizations are in the list
    obj_ids = client.list_organizations()
    for obj in created_objs:
        assert obj.id is not None
        assert obj.id in obj_ids


def test_organization_read(ckan_client_hl):
    client = ckan_client_hl

    obj_dict = generate_organization()
    obj = CkanOrganization(obj_dict)

    created = client.create_organization(obj)
    assert obj.is_equivalent(created)
    assert created.is_equivalent(obj)
