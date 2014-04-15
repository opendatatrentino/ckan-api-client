import json
import urlparse

import requests

from .exceptions import HTTPError, BadApiError
from .utils import SuppressExceptionIf


class CkanLowlevelClient(object):
    """
    Ckan low-level client.

    - Handles authentication and response validation
    - Handles request body serialization and response body deserialization
    - Raises HTTPError exceptions on failed HTTP requests
    - Performs some checks on return values from the API
    """

    def __init__(self, base_url, api_key=None):
        """
        :param basestring base_url:
            Base url for the Ckan installation
        :param basestring api_key:
            API key to be used for authentication.
            If omitted, no authentication information will be sent.
        """
        self.base_url = base_url
        self.api_key = api_key

    @property
    def anonymous(self):
        """
        Property, returning a copy of this client, without an api_key set
        """
        return CkanLowlevelClient(self.base_url)

    def request(self, method, path, **kwargs):
        """
        Wrapper around :py:func:`requests.request`.

        Extra functionality provided:

        - Add ``Authorization`` header to requests
        - If data is an object, serialize it with json and
          add the ``Content-type: application/json`` header.
        - If the response didn't contain an "ok" code,
          raises a :py:exc:`HTTPError` exception.

        :param method: HTTP method to be used
        :param path: Path, relative to the Ckan root.
            For example: ``/api/3/action/package_list``
        :param headers: HTTP headers to be added to the request
        :param data: Data to be sent in the request body
        :param kwargs: Extra keyword arguments will be passed
            directly to the ``requests.request()`` call.

        :raises ckan_api_client.exceptions.HTTPError:
            in case the HTTP request returned a non-ok status code

        :return: a requests response object
        """

        headers = kwargs.get('headers') or {}
        kwargs['headers'] = headers

        # Update headers for authorization
        if self.api_key is not None:
            headers['Authorization'] = self.api_key

        # Serialize data to json, if not already
        if 'data' in kwargs:
            if not isinstance(kwargs['data'], basestring):
                kwargs['data'] = json.dumps(kwargs['data'])
                headers['content-type'] = 'application/json'

        if isinstance(path, (list, tuple)):
            path = '/'.join(path)

        url = urlparse.urljoin(self.base_url, path)
        response = requests.request(method, url, **kwargs)
        if not response.ok:
            # ------------------------------------------------------------
            # todo: attach message, if any available..
            # ------------------------------------------------------------
            # todo: we should find a way to figure out how to attach
            #       original text message to the exception
            #       as it might be: json string, part of json object,
            #       part of html document
            # ------------------------------------------------------------
            raise HTTPError(
                status_code=response.status_code,
                message="Error while performing request",
                original=self._figure_out_error_message(response))

        return response

    def _figure_out_error_message(self, response):
        """
        We have a response, which probably contains an error message,
        but we need to figure that out..

        Usual places for errors are:

        - a json message, with {'error': {'message': ..., '__type': ...}}
        - a html page, usually when things went seriously bad
        """

        with SuppressExceptionIf(True):
            return self._figure_out_error_from_json(response.json())

    def _figure_out_error_from_json(self, data):
        if isinstance(data, dict) and 'error' in data:
            with SuppressExceptionIf(True):
                return '{0}: {1}'.format(data['error']['__type'],
                                         data['error']['message'])
            with SuppressExceptionIf(True):
                return '{0}'.format(data['error']['message'])

        raise ValueError("Unable to find message in JSON data")

    # ============================================================
    # Validation helpers
    # ============================================================

    def _validate_response_idlist(self, response, name='object'):
        if not isinstance(response, list):
            raise BadApiError(
                "Bad {0} id list returned from the api (not a list)"
                .format(name))

        if not all(isinstance(x, basestring) for x in response):
            raise BadApiError(
                "Bad {0} id list returned from the api (an element "
                "is not a string)".format(name))

    def _validate_response_dict(self, response, name='object'):
        if not isinstance(response, dict):
            raise BadApiError("Bad {0} returned from the api (not a dict)"
                              .format(name))

    def _validate_response_list_of_dict(self, response, name='object'):
        if not isinstance(response, list):
            raise BadApiError("Bad {0} list returned from the api (not a list)"
                              .format(name))

        if not all(isinstance(x, dict) for x in response):
            raise BadApiError(
                "Bad {0} list returned from the api (an element "
                "is not a dict)".format(name))

    # ============================================================
    # Datasets
    # ============================================================

    def list_datasets(self):
        """Return a list of all dataset ids"""

        path = '/api/2/rest/dataset'
        response = self.request('GET', path)
        data = response.json()
        self._validate_response_idlist(data)
        return data

    def iter_datasets(self):
        """
        Generator yielding dataset objects, iterating over the whole
        database.
        """
        for ds_id in self.list_datasets():
            yield self.get_dataset(ds_id)

    def get_dataset(self, dataset_id):
        """
        Get a dataset, using API v2

        :param dataset_id: ID of the requested dataset
        :return: a dict containing the data as returned from the API
        :rtype: dict
        """

        path = '/api/2/rest/dataset/{0}'.format(dataset_id)
        response = self.request('GET', path)
        data = response.json()
        self._validate_response_dict(data)
        return data

    def post_dataset(self, dataset):
        """
        POST a dataset, using API v2 (usually for creation)

        :param dict dataset:
            a dict containing data to be sent to Ckan.
            Should not already contain an id
        :return:
            a dict containing the data as returned from the API
        :rtype: dict
        """

        path = '/api/2/rest/dataset'
        response = self.request('POST', path, data=dataset)
        data = response.json()
        self._validate_response_dict(data)
        return data

    def put_dataset(self, dataset):
        """
        PUT a dataset, using API v2 (usually for update)

        :param dict dataset:
            a dict containing data to be sent to Ckan.
            Must contain an id, that will be used to build the URL
        :return:
            a dict containing the updated dataset as returned from the API
        :rtype: dict
        """

        path = '/api/2/rest/dataset/{0}'.format(dataset['id'])
        response = self.request('PUT', path, data=dataset)
        data = response.json()
        self._validate_response_dict(data)
        return data

    def delete_dataset(self, dataset_id, ignore_404=True):
        """
        DELETE a dataset, using API v2

        :param dataset_id: if of the dataset to be deleted
        :param bool ignore_404: if ``True`` (the default), will
            simply ignore http 404 errors from the API
        """

        ign404 = SuppressExceptionIf(
            lambda e: ignore_404 and (isinstance(e, HTTPError)
                                      and e.status_code == 404))
        path = '/api/2/rest/dataset/{0}'.format(dataset_id)
        with ign404:
            self.request('DELETE', path, data={'id': dataset_id})

    # ============================================================
    # Groups
    # ============================================================

    # =====[!!]=========== IMPORTANT NOTE ===============[!!]=====
    # BEWARE! API v2 only considers actual groups, organizations
    # are not handled / returned by this one!
    # ============================================================

    def list_groups(self):
        path = '/api/2/rest/group'
        response = self.request('GET', path)
        data = response.json()
        self._validate_response_idlist(data)
        return data

    def iter_groups(self):
        all_groups = self.list_groups()
        for group_id in all_groups:
            yield self.get_group(group_id)

    def get_group(self, group_id):
        path = '/api/2/rest/group/{0}'.format(group_id)
        response = self.request('GET', path)
        data = response.json()
        self._validate_response_dict(data)
        return data

    def post_group(self, group):
        path = '/api/2/rest/group'
        response = self.request('POST', path, data=group)
        data = response.json()
        self._validate_response_dict(data)
        return data

    def put_group(self, group):
        path = '/api/2/rest/group/{0}'.format(group['id'])
        response = self.request('PUT', path, data=group)
        data = response.json()
        self._validate_response_dict(data)
        return data

    def delete_group(self, group_id, ignore_404=True):
        ign404 = SuppressExceptionIf(
            lambda e: ignore_404 and (isinstance(e, HTTPError)
                                      and e.status_code == 404))
        path = '/api/2/rest/group/{0}'.format(group_id)
        with ign404:
            self.request('DELETE', path)
        path = '/api/3/action/group_purge'
        with ign404:
            self.request('POST', path, data={'id': group_id})

    # ============================================================
    # Organizations
    # ============================================================

    # --- [!!] NOTE ---------------------------------------------
    # We need to fallback to api v3 here, as v2 doesn't support
    # doing things with organizations..
    # ------------------------------------------------------------

    def list_organizations(self):
        path = '/api/3/action/organization_list'
        response = self.request('GET', path)
        data = response.json()['result']
        self._validate_response_idlist(data)
        return data

    def iter_organizations(self):
        for org_id in self.list_organizations():
            yield self.get_organization(org_id)

    def get_organization(self, id):
        path = '/api/3/action/organization_show?id={0}'.format(id)
        response = self.request('GET', path)
        data = response.json()['result']
        self._validate_response_dict(data)

        # API v3 returns the whole objects here, but we just
        # want the ids..
        if 'groups' in data:
            data['groups'] = [g['id'] for g in data['groups']]

        return data

    def post_organization(self, organization):
        path = '/api/3/action/organization_create'
        response = self.request('POST', path, data=organization)
        data = response.json()['result']
        self._validate_response_dict(data)
        return data

    def put_organization(self, organization):
        """Warning! with api v3 we need to use POST!"""
        path = '/api/3/action/organization_update'
        response = self.request('POST', path, data=organization)
        data = response.json()['result']
        self._validate_response_dict(data)
        return data

    def delete_organization(self, id, ignore_404=True):
        ign404 = SuppressExceptionIf(
            lambda e: ignore_404 and (isinstance(e, HTTPError)
                                      and e.status_code == 404))
        path = '/api/3/action/organization_delete'
        with ign404:
            self.request('PUT', path, data={'id': id})
        path = '/api/3/action/organization_purge'
        with ign404:
            self.request('POST', path, data={'id': id})

    # ============================================================
    # Licenses
    # ============================================================

    def list_licenses(self):
        path = '/api/2/rest/licenses'
        response = self.request('GET', path)
        data = response.json()
        self._validate_response_list_of_dict(data)
        return data
