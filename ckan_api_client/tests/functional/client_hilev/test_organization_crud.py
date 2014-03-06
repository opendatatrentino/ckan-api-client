"""
Tests for organization crud, using high-level client.
"""

import pytest

from ckan_api_client.tests.utils.generate import generate_organization
from ckan_api_client.objects import CkanOrganization


@pytest.mark.xfail(run=False, reason='Requires CkanOrganization')
def test_organization_create(ckan_client_hl):
    client = ckan_client_hl

    obj_dict = generate_organization()
    obj = CkanOrganization(obj_dict)

    created = client.create_organization(obj)
    assert obj.is_equivalent(created)
    assert created.is_equivalent(obj)


@pytest.mark.xfail(run=False, reason='Requires CkanOrganization')
def test_organization_list(ckan_client_hl):
    client = ckan_client_hl

    ## Create a bunch of organizations
    obj_dicts = [generate_organization() for _ in xrange(10)]
    objs = [CkanOrganization.from_dict(d) for d in obj_dicts]
    created_objs = [client.create_organization(o) for o in objs]

    ## Make sure all the orgnaizations are in the list
    obj_ids = client.list_organizations()
    for obj in created_objs:
        assert obj.id is not None
        assert obj.id in obj_ids


@pytest.mark.xfail(run=False, reason='Requires CkanOrganization')
def test_organization_read(ckan_client_hl):
    client = ckan_client_hl

    obj_dict = generate_organization()
    obj = CkanOrganization(obj_dict)

    created = client.create_organization(obj)
    assert obj.is_equivalent(created)
    assert created.is_equivalent(obj)
