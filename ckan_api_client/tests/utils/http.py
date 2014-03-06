"""Utilities for handling / checking HTTP responses"""

import cgi
import warnings


def check_response_ok(response, status_code=200):
    """
    .. warning:: deprecated function. Use :py:func:`check_api_v3_response`.
    """
    warnings.warn(
        "check_response_ok() is deprecated -- use check_api_v3_response()",
        DeprecationWarning)
    return check_api_v3_response(response, status_code=status_code)


def check_response_error(response, status_code):
    """
    .. warning:: deprecated function. Use :py:func:`check_api_v3_error`.
    """
    warnings.warn(
        "check_response_ok() is deprecated -- use check_api_v3_error()",
        DeprecationWarning)
    return check_api_v3_error(response, status_code=status_code)


def check_api_v3_response(response, status_code=200):
    """
    Make sure that ``response`` is a valid successful response
    from API v3.

    - check http status code to be in the 200-299 range
    - check http status code to match ``status_code``
    - check content-type to be application/json
    - check charset to be utf-8
    - check content body to be valid json
    - make sure response object contains the ``success``,
      ``result`` and ``help`` keys.
    - check that ``success`` is True
    - check that ``error`` key is not in the response

    :param response: a ``requests`` response
    :param status_code: http status code to be checked
        (default: 200)
    """
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


def check_api_v3_error(response, status_code):
    """
    Make sure that ``response`` is a valid error response from
    API v3.

    - check http status code to match ``status_code``

    :param response: a ``requests`` response
    :param status_code: http status code to be checked
    """

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
