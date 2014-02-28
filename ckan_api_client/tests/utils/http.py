"""Utilities for handling / checking HTTP responses"""

import cgi


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
