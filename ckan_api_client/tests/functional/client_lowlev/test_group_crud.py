import copy

import pytest

from ckan_api_client.exceptions import HTTPError
from .utils import ckan_client  # noqa (fixture)
from .utils import check_group, gen_random_id, get_dummy_group


def test_group_crud(ckan_client):
    code = gen_random_id()
    group = {
        'name': 'group-{0}'.format(code),
        'title': 'Group {0}'.format(code),
    }
    created = ckan_client.post_group(group)
    check_group(created, group)
    group_id = created['id']

    # Retrieve & check
    retrieved = ckan_client.get_group(group_id)
    assert retrieved == created

    # Update & check
    updated = ckan_client.put_group({'id': group_id, 'title': 'My Group'})
    assert updated['name'] == group['name']
    assert updated['title'] == 'My Group'

    # Check differences
    expected = copy.deepcopy(created)
    expected['title'] = 'My Group'
    check_group(updated, expected)

    # Retrieve & double-check
    retrieved = ckan_client.get_group(group_id)
    assert retrieved == updated

    # Delete
    #------------------------------------------------------------
    # Note: it's impossible to actually delete a group.
    #       The only hint it has been deleted is its "state"
    #       is set to "deleted".
    #------------------------------------------------------------
    ckan_client.delete_group(group_id)

    with pytest.raises(HTTPError) as excinfo:
        ckan_client.get_group(group_id)
    assert excinfo.value.status_code in (404, 403)  # workaround

    # retrieved = ckan_client.get_group(group_id)
    # assert retrieved['state'] == 'deleted'

    # anon_client = ckan_client.anonymous
    # # with pytest.raises(HTTPError) as excinfo:
    # #     anon_client.get_group(group_id)
    # # assert excinfo.value.status_code in (404, 403)  # workaround
    # retrieved = anon_client.get_group(group_id)
    # assert retrieved['state'] == 'deleted'


def test_simple_group_crud(ckan_client):
    ## Let's try creating a dataset

    _group = get_dummy_group(ckan_client)

    group = ckan_client.post_group(_group)
    group_id = group['id']

    ## Let's check group data first..
    for key, val in _group.iteritems():
        assert group[key] == val

    ## Check that retrieved group is identical
    group = ckan_client.get_group(group_id)
    for key, val in _group.iteritems():
        assert group[key] == val

    ## Check against data loss on update..
    retrieved_group = group
    updates = {
        'title': 'New group title',
        'description': 'New group description',
    }
    new_group = copy.deepcopy(group)
    new_group.update(updates)
    new_group['id'] = group_id

    ## Get the updated group
    updated_group = ckan_client.put_group(new_group)
    updated_group_2 = ckan_client.get_group(group_id)

    ## They should be equal!
    assert updated_group == updated_group_2

    ## And the updated group shouldn't have data loss
    expected_group = copy.deepcopy(retrieved_group)
    expected_group.update(updates)

    check_group(updated_group, expected_group)

    # for f in GROUP_FIELDS['cruft']:
    #     updated_group.pop(f, None)
    #     expected_group.pop(f, None)

    # assert updated_group == expected_group

    ## Delete the group
    ckan_client.delete_group(group_id)
