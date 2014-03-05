# -*- coding: utf-8 -*-

##-----------------------------------------------------------------------------
## Note: all the places in which an undesired behavior is going on are marked
## as ``FIXME:``, to mark a pending upstream fix.
##-----------------------------------------------------------------------------

import cgi
# import copy
import random

import pytest

from .utils import CkanClient


DUMMY_PACKAGES = {}
DUMMY_PACKAGES['simplest_package'] = {
    'name': 'hello-dataset',
    'title': 'Hello, dataset!',
}
DUMMY_PACKAGES['package_with_metadata'] = {
    'name': 'package-with-metadata',
    'title': 'Package with metadata',
    'author': 'Author Name',
    'author_email': 'author.name@example.com',
    'maintainer': 'Maintainer Name',
    'maintainer_email': 'maintainer.name@example.com',
    'license_id': 'cc-by',
    'notes': 'Just a bunch of notes',
    'url': 'http://example.com/dataset/package-with-metadata',
    'state': 'active',
    #'type': 'dataset',

    #'resources': [],
    #'tags': [],
    #'extras': [{'key': 'Fuck', 'value': 'This!'}],
    #'groups': [],
    #'owner_org': ['dummy-org'],
}
DUMMY_PACKAGES['package_with_extras'] = {
    'name': 'package-with-extras',
    'title': 'Package with extras',
    'author': 'Author Name',
    'author_email': 'author.name@example.com',
    'maintainer': 'Maintainer Name',
    'maintainer_email': 'maintainer.name@example.com',
    'license_id': 'cc-by',
    'notes': 'Just a bunch of notes',
    'url': 'http://example.com/dataset/package-with-extras',
    'state': 'active',

    'extras': [
        {'key': 'Extra field #1', 'value': 'Extra value #1'},
        {'key': 'Extra field #2', 'value': 'Extra value #2'},
        {'key': 'Extra field #3', 'value': 'Extra value #3'},
    ],
}
DUMMY_PACKAGES['package_with_tags'] = {
    'name': 'package-with-tags',
    'title': 'Package with tags',
    'license_id': 'cc-by',
    'url': 'http://example.com/dataset/package-with-tags',
    'state': 'active',

    'tags': [
        {'name': 'Tag One'},
        {'name': 'Tag Two'},
        {'name': 'Tag Three'},
    ],
}


def get_sysadmin_api_key(ckan_env):
    """Create a sysadmin user, return its API key"""

    user_name = 'api_test_{0:06d}'.format(random.randint(0, 10**6))
    user_data = ckan_env.paster_user_add(user_name, **{
        'password': 'password',
        'email': '{0}@example.com'.format(user_name)})
    ckan_env.paster_sysadmin_add(user_name)
    return user_data['apikey']


def check_response(response, code=200, success=True):
    """
    Make sure an API response is ok:

    - check that status code is in the "ok" range
    - check status code (default: 200)
    - check content-type header (must be application/json)
    - check that response data is valid json
    - check that response data has a 'success' key with True value
    - check that response data has a 'result' key

    :param response: Response object from the requests module
    :type response: requests.models.Response
    :param int code: expected HTTP status code
    :param bool success: wheter we expect success or failure
    :return: the decoded (json) response data
    """
    if type(success) != bool:
        raise TypeError('success must be a boolean')

    assert response.ok is success
    assert response.status_code == code
    content_type = cgi.parse_header(response.headers['content-type'])[0]
    assert content_type == 'application/json'
    data = response.json()
    assert data['success'] is success
    if success:
        assert 'result' in data
    else:
        assert 'error' in data
    return data


def check_dataset(expected, actual):
    """
    Check that values in "actual" match the ones in "expected".
    """

    assert 'id' in actual
    assert isinstance(expected, dict)
    assert isinstance(actual, dict)

    if 'id' in expected:
        assert actual['id'] == expected['id']

    ## Make sure everything is ok
    for key, value in expected.iteritems():
        if key == 'tags':
            check_dataset_tags(expected[key], actual[key])

        elif key == 'extras':
            ## todo: we should check that, for example, we don't have
            ##       duplicate keys...
            assert sorted(actual[key]) == sorted(value)

        elif key == 'resources':
            check_dataset_resources(expected[key], actual[key])

        else:
            ## This key is not to be handled in a special way
            assert actual[key] == expected[key]


def check_dataset_resources(expected, actual):
    ## We need to check only the fields specified in the
    ## "expected" object. But we need to reorder resources
    ## in a dictionary to compare..
    assert len(actual) == len(expected)

    ## We group them by name as the id is generated, so we can't
    ## expect one..
    expected_resources = dict((r['name'], r) for r in expected)
    assert len(expected) == len(expected_resources)

    actual_resources = dict((r['name'], r) for r in actual)
    assert len(actual) == len(actual_resources)

    for res_id in expected_resources:
        expected_resource = expected_resources[res_id]
        actual_resource = actual_resources[res_id]
        for key_id in expected_resource:
            assert expected_resource[key_id] \
                == actual_resource[key_id]


def check_dataset_tags(expected, actual):
    ## Tags have a lot of extra fields, we only care about some of them..
    expected_tags = sorted(x['name'] for x in expected)
    actual_tags = sorted(x['name'] for x in actual)
    assert actual_tags == expected_tags


@pytest.fixture(params=sorted(DUMMY_PACKAGES.keys()))
def dummy_package(request):
    return DUMMY_PACKAGES[request.param]


## Actual test functions
##------------------------------------------------------------


def test_simple_package_crud(ckan_env):
    API_KEY = get_sysadmin_api_key(ckan_env)

    with ckan_env.serve() as server:
        client = CkanClient(server.url, api_key=API_KEY)
        anon_client = CkanClient(server.url)

        # Create a dataset
        # url = urlparse.urljoin(server.url, '/api/3/action/package_create')
        data = {
            'name': 'my-first-dataset',
            'title': 'My First Dataset',
        }
        # response = post_json(url, API_KEY, data)
        response = client.post('/api/3/action/package_create', data=data)
        assert response.ok

        # should be 201 CREATED or 303 FOUND
        assert response.status_code == 200

        data = response.json()
        assert data['success'] is True
        dataset_id = data['result']['id']

        # Get it back
        response = client.get('/api/3/action/package_show?id={0}'
                              .format(dataset_id))
        data = check_response(response)
        assert 'result' in data
        assert data['result']['id'] == dataset_id

        ## Delete the dataset
        ##------------------------------------------------------------

        response = client.post('/api/3/action/package_delete',
                               data={'id': dataset_id})
        check_response(response)

        ## Make sure the package has been actually deleted
        ##------------------------------------------------------------

        # Anonymous users should get a 404
        response = anon_client.get('/api/3/action/package_show?id={0}'
                                   .format(dataset_id))

        ## FIXME: Dammit, this is returning 403 -> should return 404!!
        #data = check_response(response, code=404, success=False)
        data = check_response(response, code=403, success=False)

        # An this should also be gone form the list
        response = anon_client.get('/api/3/action/package_list')
        data = check_response(response)
        assert isinstance(data['result'], list)
        assert dataset_id not in data['result']

        # Sysadmin users are still able to see the deleted package
        # FIXME: this behavior might be confusing -> I'd still return 404
        response = client.get('/api/3/action/package_show?id={0}'
                              .format(dataset_id))
        data = check_response(response)
        assert data['result']['state'] == 'deleted'

        # An this should also be gone form the list
        response = anon_client.get('/api/3/action/package_list')
        data = check_response(response)
        assert isinstance(data['result'], list)
        assert dataset_id not in data['result']


def test_package_creation(ckan_env, dummy_package):
    """
    Create a dataset, retrieve it and check
    """

    API_KEY = get_sysadmin_api_key(ckan_env)

    with ckan_env.serve() as server:
        client = CkanClient(server.url, api_key=API_KEY)
        response = client.post(
            '/api/3/action/package_create', data=dummy_package)
        assert response.ok

        ## although this should be 201 CREATED or 303 FOUND
        assert response.status_code == 200

        data = response.json()
        assert data['success'] is True
        dataset_id = data['result']['id']

        # Get it back
        response = client.get('/api/3/action/package_show?id={0}'
                              .format(dataset_id))
        assert response.ok
        assert response.status_code == 200
        assert data['success'] is True
        assert 'result' in data
        assert data['result']['id'] == dataset_id

        ## Check that keys match
        for key in dummy_package:
            if key in ('tags',):
                continue
            assert data['result'][key] == dummy_package[key]

        ## Check that tags match
        if 'tags' in dummy_package:
            expected_tags = sorted(x['name'] for x in dummy_package['tags'])
            actual_tags = sorted(x['name'] for x in data['result']['tags'])
            assert actual_tags == expected_tags

        # # Delete the dataset
        # # url = urlparse.urljoin(server.url, '/api/3/action/package_delete')
        # # response = json_request('post', url, API_KEY, {'id': dataset_id})
        # response = client.post('/api/3/action/package_delete',
        #                        data={'id': dataset_id})
        # assert response.ok


def test_real_case_scenario(ckan_env):
    """
    "Real case" scenario:

    - create an organization
    - add some datasets associated with the organization
    - check state
    - update datasets (add, update, delete)
    - check state

    """

    state = {}
    state[0] = {
        'http://www.example.com/dataset-1': {
            'name': 'dataset-1',
            'title': 'Dataset #1',
            'info': {
                'key_1': 'value_1',
                'key_2': 'value_2',
            },
            'resources': [
                {'url': 'http://www.example.com/dataset-1/resource1.json',
                 'mimetype': 'application/json'},
                {'url': 'http://www.example.com/dataset-1/resource2.json',
                 'mimetype': 'application/json'},
            ]
        }
    }

    API_KEY = get_sysadmin_api_key(ckan_env)

    with ckan_env.serve() as server:
        client = CkanClient(server.url, api_key=API_KEY)

        ## Create our organization
        response = client.post('/api/3/action/organization_create', data={
            'name': 'my-organization',
            'title': 'My organization',
        })
        assert response.ok
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        organization_id = data['result']['id']

        ## Get the organization back
        response = client.get('/api/3/action/organization_show?id={0}'
                              .format(organization_id))
        assert response.ok
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'result' in data
        assert data['result']['id'] == organization_id

        def create_dataset(data):
            """
            Create a dataset and check that everything is ok

            :param data: Data for the dataset to be created
            :return: The created dataset object
            """

            ## Create dataset
            response = client.post('/api/3/action/package_create', data=data)
            data = check_response(response)
            dataset_id = data['result']['id']

            ## Get the dataset back and check
            response = client.get('/api/3/action/package_show?id={0}'
                                  .format(dataset_id))
            data = check_response(response)
            assert data['result']['id'] == dataset_id

            return data['result']

        ## Create a dataset
        ##------------------------------------------------------------

        dataset_obj = {
            'name': 'dataset-1',
            'title': 'Dataset #1',
            'url': 'http://example.com/dataset-1',
            'state': 'active',
            'license_id': 'cc-zero',
            'notes': 'Some notes for the first dataset',
            'owner_org': organization_id,
            'extras': [
                {'key': 'extra0', 'value': 'Extra value #0'},
                {'key': 'extra1', 'value': 'Extra value #1'},
            ]
        }
        dataset = create_dataset(dataset_obj)
        dataset_id = dataset['id']

        ## Now we should try updating
        ##------------------------------------------------------------
        ## Note: apparently there is no way to update just *some*
        ##       metadata: we have to send the whole object again..
        ## todo: check whether we should pass even resources / tags
        ##       / extras too...

        ## Note: we need some better way to check what's going on;
        ## we need to determine / make sure *which* fields should be sent
        ## back during the update, which have no effect, which are ignored,
        ## etc.
        ## Also, we need to make sure on how exactly the "extra" field
        ## works..

        dataset_obj['title'] = 'First dataset'
        dataset_obj['notes'] = 'Updated notes here!'

        response = client.post(
            '/api/3/action/dataset_update?id={0}'.format(dataset_id),
            data=dataset_obj)
        data = check_response(response)
        updated_dataset = data['result']
        check_dataset(dataset_obj, updated_dataset)

        ## Now get it from the API
        response = client.get(
            '/api/3/action/dataset_show?id={0}'.format(dataset_id))
        data = check_response(response)
        updated_dataset = data['result']
        check_dataset(dataset_obj, updated_dataset)

        ## Just to be extra safe..
        assert updated_dataset['title'] == 'First dataset'
        assert updated_dataset['notes'] == 'Updated notes here!'
        assert updated_dataset['url'] == 'http://example.com/dataset-1'
        assert updated_dataset['license_id'] == 'cc-zero'

        ## Ok, now we should try updating extras too..
        ##------------------------------------------------------------
