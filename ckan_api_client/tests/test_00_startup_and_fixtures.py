"""Make sure tests setup & fixtures are all fine"""

import requests

from .utils.http import check_response_ok

# todo: we should check all fixtures in here!


def test_site_read(ckan_url):
    """GET /site_read/ should return 200"""

    api_url = ckan_url('/api/3/action/site_read')
    response = requests.get(api_url)
    data = check_response_ok(response)
    assert data['result'] is True

    # Call to an invalid URL should return 404
    response = requests.get(ckan_url('/api/3/action/site_read/something'))

    assert not response.ok
    assert response.status_code == 404
