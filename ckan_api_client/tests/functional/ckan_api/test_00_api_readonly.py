"""
Tests to check that Ckan behaves correctly on an empty database.
"""

import cgi

import pytest
import requests


def check_response_ok(response, status_code=200):
    assert response.ok
    assert response.status_code == status_code

    # The API should always return json!
    content_type = cgi.parse_header(response.headers['content-type'])
    assert content_type[0] == 'application/json'
    assert content_type[1]['charset'] == 'utf-8'
    data = response.json()

    # This thing was successful!
    assert data['success'] is True
    assert 'result' in data
    assert 'error' not in data
    assert 'help' in data  # :(

    return data


def check_response_error(response, status_code):
    assert not response.ok
    assert response.status_code == status_code

    # Should return json anyways..
    content_type = cgi.parse_header(response.headers['content-type'])
    assert content_type[0] == 'application/json'
    assert content_type[1]['charset'] == 'utf-8'
    data = response.json()

    # This is an error!
    assert data['success'] is False
    assert 'error' in data
    assert 'result' not in data

    return data


def test_site_read(ckan_url):
    """GET /site_read/ should return 200"""

    api_url = ckan_url('/api/3/action/site_read')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert data['result'] is True

    ## Call to an invalid URL should return 404
    response = requests.get(ckan_url('/api/3/action/site_read/something'))
    assert not response.ok
    assert response.status_code == 404


def test_invalid_method_name(ckan_url):
    """Call to an invalid method name should return 404"""

    api_url = ckan_url('/api/3/action/invalid_method_name')
    response = requests.get(api_url)
    assert not response.ok
    assert response.status_code == 400


def test_package_list(ckan_url):
    """GET /package_list/ should return an empty list"""

    api_url = ckan_url('/api/3/action/package_list')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert data['result'] == []

    api_url = ckan_url('/api/3/action/package_list?limit=10')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert data['result'] == []

    api_url = ckan_url('/api/3/action/package_list?offset=10&limit=20')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert data['result'] == []

    ## Right now, invalid arguments are just ignored..
    api_url = ckan_url('/api/3/action/package_list?invalid=hello')
    response = requests.get(api_url)
    data = check_response_ok(response)


def test_current_package_list_with_resources(ckan_url):
    """GET /current_package_list_with_resources/ should return empty list"""

    api_url = ckan_url('/api/3/action/current_package_list_with_resources')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert data['result'] == []

    api_url = ckan_url('/api/3/action/current_package_list_with_resources')

    response = requests.get(api_url + '?limit=10')
    data = check_response_ok(response)
    assert data['result'] == []

    response = requests.get(api_url + '?limit=10&offset=20')
    data = check_response_ok(response)
    assert data['result'] == []

    response = requests.get(api_url + '?offset=20')
    data = check_response_ok(response)
    assert data['result'] == []


def test_revision_list(ckan_url):
    """GET /revision_list/"""

    api_url = ckan_url('/api/3/action/revision_list')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert isinstance(data['result'], list)

    # todo: how do we check this? why two revisions?
    assert len(data['result']) == 2


@pytest.mark.xfail
def test_package_revision_list_without_id(ckan_url):
    """
    GET /package_revision_list/ w/o an id

    Expected: 400
    """

    api_url = ckan_url('/api/3/action/package_revision_list')
    response = requests.get(api_url)
    check_response_error(response, 400)


def test_package_revision_list_id_non_existing(ckan_url):
    """
    GET /package_revision_list/ with id of a non-existing object,

    Expected: 404
    """

    api_url = ckan_url('/api/3/action/package_revision_list'
                       '?id=00000000-0000-0000-0000-000000000000')
    response = requests.get(api_url)
    check_response_error(response, 404)

    # This should return 404 too..
    api_url = ckan_url('/api/3/action/package_revision_list?id=missing_object')
    response = requests.get(api_url)
    check_response_error(response, 404)


@pytest.mark.xfail
def test_related_show_without_id(ckan_url):
    api_url = ckan_url('/api/3/action/related_show')
    response = requests.get(api_url)
    check_response_error(response, 404)


def test_related_show_id_non_existing(ckan_url):
    api_url = ckan_url('/api/3/action/related_show'
                       '?id=00000000-0000-0000-0000-000000000000')
    response = requests.get(api_url)
    check_response_error(response, 404)

    api_url = ckan_url('/api/3/action/related_show?id=missing_object')
    response = requests.get(api_url)
    check_response_error(response, 404)


def test_related_list(ckan_url):
    api_url = ckan_url('/api/3/action/related_list')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert data['result'] == []


@pytest.mark.xfail
def test_related_list_id_non_existing(ckan_url):
    ## related_list?id=invalid
    ## With an invalid id, should return 404 (but wouldn't!)
    api_url = ckan_url('/api/3/action/related_list?id=invalid')
    response = requests.get(api_url)
    check_response_error(response, 404)


@pytest.mark.xfail
def test_member_list_without_id(ckan_url):
    api_url = ckan_url('/api/3/action/member_list')
    response = requests.get(api_url)
    check_response_error(response, 404)


def test_member_list_id_non_existing(ckan_url):
    api_url = ckan_url('/api/3/action/member_list'
                       '?id=00000000-0000-0000-0000-000000000000')
    response = requests.get(api_url)
    check_response_error(response, 404)

    api_url = ckan_url('/api/3/action/member_list?id=missing_object')
    response = requests.get(api_url)
    check_response_error(response, 404)


def test_group_list(ckan_url):
    api_url = ckan_url('/api/3/action/group_list')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert data['result'] == []


def test_organization_list(ckan_url):
    api_url = ckan_url('/api/3/action/organization_list')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert data['result'] == []


def test_group_list_authz(ckan_url):
    api_url = ckan_url('/api/3/action/group_list_authz')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert data['result'] == []


def test_organization_list_for_user(ckan_url):
    api_url = ckan_url('/api/3/action/organization_list_for_user')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert data['result'] == []


@pytest.mark.xfail
def test_group_revision_list(ckan_url):
    api_url = ckan_url('/api/3/action/group_revision_list')
    response = requests.get(api_url)
    check_response_error(response, 400)  # Missing id

    api_url = ckan_url('/api/3/action/group_revision_list?id=does-not-exist')
    response = requests.get(api_url)
    check_response_error(response, 404)  # Non-existing id


def test_license_list(ckan_url):
    api_url = ckan_url('/api/3/action/license_list')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert isinstance(data['result'], list)
    for item in data['result']:
        assert isinstance(item, dict)


def test_tag_list(ckan_url):
    api_url = ckan_url('/api/3/action/tag_list')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert data['result'] == []

    api_url = ckan_url('/api/3/action/tag_list?vocabulary_id=does-not-exist')
    response = requests.get(api_url)
    check_response_error(response, 404)


def test_user_list(ckan_url):
    api_url = ckan_url('/api/3/action/user_list')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert isinstance(data['result'], list)
    for item in data['result']:
        assert isinstance(item, dict)
    assert len(data['result']) == 3

    user_names = [x['name'] for x in data['result']]
    assert 'logged_in' in user_names
    assert 'visitor' in user_names
    # todo: what about the third one?? wtf is that for??
    # [u'ckan_bb_testing', u'logged_in', u'visitor']
