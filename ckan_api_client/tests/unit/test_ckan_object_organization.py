"""Unit tests for CkanOrganization object"""

import json

import pytest

from ckan_api_client.objects import CkanOrganization
from ckan_api_client.utils import freeze

dummy_org = freeze({
    'name': 'my-organization',
    'title': 'My Organization',
    'description': 'Description of organization 1w1ah41d7l',
    'image_url': 'http://robohash.org/1be192563ce3bc70c26fd36d98089dde.png',
    'approval_status': 'approved',
})


@pytest.mark.xfail(run=False, reason='WIP')
def test_ckan_organization_creation():
    organization = CkanOrganization(dummy_org)
    assert organization.name == 'my-organization'
    assert organization.title == 'My Organization'
    assert organization.description == 'My org description'

    # Make sure it can be json-serialized
    serialized = organization.serialize()
    json.dumps(serialized)


# todo: write further tests
