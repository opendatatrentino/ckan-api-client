"""
Low-level ckan API client
"""

import json
import urlparse
import warnings

import requests

from .exceptions import HTTPError, BadApiError, BadApiWarning
from .utils import SuppressExceptionIf
from .schema import DATASET_FIELDS, RESOURCE_FIELDS, GROUP_FIELDS


class CkanLowlevelClient(object):
    """Ckan low-level client.

    - Handles authentication and response validation.
    - Raises HTTPError exceptions on failed HTTP requests.
    """

    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.api_key = api_key

    @property
    def anonymous(self):
        """Return a copy of this client, without api_key"""
        return CkanLowlevelClient(self.base_url)

    def request(self, method, path, **kwargs):
        headers = kwargs.get('headers') or {}
        kwargs['headers'] = headers

        ## Update headers for authorization
        if self.api_key is not None:
            headers['Authorization'] = self.api_key

        ## Serialize data to json, if not already
        if 'data' in kwargs:
            if not isinstance(kwargs['data'], basestring):
                kwargs['data'] = json.dumps(kwargs['data'])
                headers['content-type'] = 'application/json'

        if isinstance(path, (list, tuple)):
            path = '/'.join(path)

        url = urlparse.urljoin(self.base_url, path)
        response = requests.request(method, url, **kwargs)
        if not response.ok:
            ## todo: attach message, if any available..
            ## todo: we should find a way to figure out how to attach
            ##       original text message to the exception
            ##       as it might be: json string, part of json object,
            ##       part of html document
            raise HTTPError(response.status_code,
                            "Error while performing request")

        return response

    ##============================================================
    ## Datasets
    ##============================================================

    def list_datasets(self):
        path = '/api/2/rest/dataset'
        response = self.request('GET', path)
        data = response.json()

        ## Check response value
        if not isinstance(data, list):
            raise BadApiError("Dataset list didn't return a list")
        if not all(isinstance(x, basestring) for x in data):
            raise BadApiError("Dataset list is not a list of strings")

        return data

    def iter_datasets(self):
        for ds_id in self.list_datasets():
            yield self.get_dataset(ds_id)

    def get_dataset(self, dataset_id):
        if not isinstance(dataset_id, basestring):
            raise ValueError("dataset_id must be a string")

        path = '/api/2/rest/dataset/{0}'.format(dataset_id)
        response = self.request('GET', path)
        data = response.json()

        ## Check response value
        if not isinstance(data, dict):
            raise BadApiError("Dataset returned from API is not a dict")

        return data

    def post_dataset(self, dataset):
        path = '/api/2/rest/dataset'
        response = self.request('POST', path, data=dataset)
        data = response.json()

        if not isinstance(data, dict):
            raise BadApiError("Dataset returned from API is not a dict")

        return data

    def put_dataset(self, dataset_id, dataset):
        """
        PUT a dataset (for update).

        .. warning::

            ``update_dataset()`` should be used instead, in normal cases,
            as it automatically takes care of a lot of needed workarounds
            to prevent data loss.

            Calling this method directly is almost never adviced or required.
        """
        path = '/api/2/rest/dataset/{0}'.format(dataset_id)
        response = self.request('PUT', path, data=dataset)
        data = response.json()

        if not isinstance(data, dict):
            raise BadApiError("Dataset returned from API is not a dict")

        return data

    def delete_dataset(self, dataset_id, ignore_404=True):
        ign404 = SuppressExceptionIf(
            lambda e: ignore_404 and (e.status_code == 404))
        path = '/api/2/rest/dataset/{0}'.format(dataset_id)
        with ign404:
            self.request('DELETE', path, data={'id': dataset_id})

    ##============================================================
    ## Groups
    ##============================================================

    ##=====[!!]=========== IMPORTANT NOTE ===============[!!]=====
    ## BEWARE! API v2 only considers actual groups, organizations
    ## are not handled / returned by this one!
    ##============================================================

    @check_retval(is_list_of(basestring))
    def list_groups(self):
        path = '/api/2/rest/group'
        response = self.request('GET', path)
        return response.json()

    def iter_groups(self):
        all_groups = self.list_groups()
        for group_id in all_groups:
            yield self.get_group(group_id)

    @check_arg_types(None, basestring)
    @check_retval(dict)
    def get_group(self, group_id):
        path = '/api/2/rest/group/{0}'.format(group_id)
        response = self.request('GET', path)
        return response.json()

    @check_arg_types(None, dict)
    @check_retval(dict)
    def post_group(self, group):
        path = '/api/2/rest/group'
        response = self.request('POST', path, data=group)
        return response.json()

    @check_arg_types(None, basestring, dict)
    @check_retval(dict)
    def put_group(self, group_id, group):
        path = '/api/2/rest/group/{0}'.format(group_id)
        response = self.request('PUT', path, data=group)
        data = response.json()
        return data

    @check_arg_types(None, basestring, ignore_404=bool)
    def delete_group(self, group_id, ignore_404=True):
        ign404 = SuppressExceptionIf(
            lambda e: ignore_404 and (e.status_code == 404))
        path = '/api/2/rest/group/{0}'.format(group_id)
        with ign404:
            self.request('DELETE', path)
        path = '/api/3/action/group_purge'
        with ign404:
            self.request('POST', path, data={'id': group_id})

    @check_arg_types(None, basestring, dict)
    @check_retval(dict)
    def update_group(self, group_id, updates):
        """
        Trickery to perform a safe partial update of a group.
        """

        original_group = self.get_group(group_id)

        ## Dictionary holding the actual data to be sent
        ## for performing the update
        updates_dict = {'id': group_id}

        ##------------------------------------------------------------
        ## Core fields
        ##------------------------------------------------------------

        for field in GROUP_FIELDS['core']:
            if field in updates:
                updates_dict[field] = updates[field]
            else:
                updates_dict[field] = original_group[field]

        ##------------------------------------------------------------
        ## Extras fields
        ##------------------------------------------------------------

        ## We assume the same behavior here as for datasets..
        ## See update_dataset() for more details.

        EXTRAS_FIELD = 'extras'  # to avoid confusion

        updates_dict[EXTRAS_FIELD] = {}

        if EXTRAS_FIELD in updates:
            # Notes: setting a field to 'None' will delete it.
            updates_dict[EXTRAS_FIELD].update(updates[EXTRAS_FIELD])

        ## These fields need to be passed again or they will just
        ## be flushed..
        FIELDS_THAT_NEED_TO_BE_PASSED = [
            'groups',  # 'tags'?
        ]
        for field in FIELDS_THAT_NEED_TO_BE_PASSED:
            if field in updates:
                updates_dict[field] = updates[field]
            else:
                updates_dict[field] = original_group[field]

        ## Actually perform the update
        ##----------------------------------------

        return self.put_group(group_id, updates_dict)

    @check_arg_types(None, dict)
    @check_retval(dict)
    def upsert_group(self, group):
        """
        Try to "upsert" a group, by name.

        This will:
        - retrieve the group
        - if the group['state'] == 'deleted', try to restore it
        - if something changed, update it

        :return: the group object
        """

        # Try getting group..
        if 'id' in group:
            raise ValueError("You shouldn't specify a group id already!")

        ## Get the group
        ## Groups should be returned by name too (hopefully..)
        try:
            _retr_group = self.get_group(group['name'])
        except HTTPError:
            _retr_group = None

        if _retr_group is None:
            ## Just insert the group and return its id
            return self.post_group(group)

        updates = {}
        if _retr_group['state'] == 'deleted':
            ## We need to make it active again!
            updates['state'] = 'active'

        ## todo: Check if we have differences, before updating!

        updated_dict = copy.deepcopy(group)
        updated_dict.update(updates)

        return self.update_group(_retr_group['id'], updated_dict)

    ##============================================================
    ## Organizations
    ##============================================================

    ## --- [!!] NOTE ---------------------------------------------
    ## We need to fallback to api v3 here, as v2 doesn't support
    ## doing things with organizations..
    ##------------------------------------------------------------

    @check_retval(is_list_of(basestring))
    def list_organizations(self):
        path = '/api/3/action/organization_list'
        response = self.request('GET', path)
        return response.json()['result']

    def iter_organizations(self):
        for org_id in self.list_organizations():
            yield self.get_organization(org_id)

    @check_arg_types(None, basestring)
    @check_retval(dict)
    def get_organization(self, organization_id):
        path = '/api/3/action/organization_show?id={0}'.format(organization_id)
        response = self.request('GET', path)
        return response.json()['result']

    @check_retval(dict)
    def post_organization(self, organization):
        path = '/api/3/action/organization_create'
        response = self.request('POST', path, data=organization)
        return response.json()['result']

    @check_retval(dict)
    def put_organization(self, organization_id, organization):
        """Warning! with api v3 we need to use POST!"""
        organization['id'] = organization_id
        path = '/api/3/action/organization_update'
        response = self.request('POST', path, data=organization)
        return response.json()['result']

    @check_arg_types(None, basestring, dict)
    @check_retval(dict)
    def update_organization(self, organization_id, updates):
        """
        Trickery to perform a safe partial update of a organization.
        """

        original_organization = self.get_organization(organization_id)

        ## Dictionary holding the actual data to be sent
        ## for performing the update
        updates_dict = {'id': organization_id}

        ##------------------------------------------------------------
        ## Core fields
        ##------------------------------------------------------------

        for field in GROUP_FIELDS['core']:
            if field in updates:
                updates_dict[field] = updates[field]
            else:
                updates_dict[field] = original_organization[field]

        ##------------------------------------------------------------
        ## Extras fields
        ##------------------------------------------------------------

        ## We assume the same behavior here as for datasets..
        ## See update_dataset() for more details.

        # EXTRAS_FIELD = 'extras'  # to avoid confusion

        # # updates_dict[EXTRAS_FIELD] = {}
        # updates_dict[EXTRAS_FIELD] = [{}]  # BUG!!

        # if EXTRAS_FIELD in updates:
        #     # Notes: setting a field to 'None' will delete it.
        #     # updates_dict[EXTRAS_FIELD].update(updates[EXTRAS_FIELD])
        #     updates_dict[EXTRAS_FIELD] = [updates[EXTRAS_FIELD]]

        ## Fuck this

        ## These fields need to be passed again or they will just
        ## be flushed..
        FIELDS_THAT_NEED_TO_BE_PASSED = [
            'groups',  # 'tags'?
        ]
        for field in FIELDS_THAT_NEED_TO_BE_PASSED:
            if field in updates:
                updates_dict[field] = updates[field]
            else:
                updates_dict[field] = original_organization[field]

        ## Actually perform the update
        ##----------------------------------------

        return self.put_organization(organization_id, updates_dict)

    @check_arg_types(None, dict)
    @check_retval(dict)
    def upsert_organization(self, organization):
        """
        Try to "upsert" a organization, by name.

        This will:
        - retrieve the organization
        - if the organization['state'] == 'deleted', try to restore it
        - if something changed, update it

        :return: the organization object
        """

        # Try getting organization..
        if 'id' in organization:
            raise ValueError(
                "You shouldn't specify a organization id! "
                "Name is going to be used as upsert key.")

        ## Get the organization
        ## Groups should be returned by name too (hopefully..)
        try:
            _retr_organization = self.get_organization(organization['name'])
        except HTTPError:
            _retr_organization = None

        if _retr_organization is None:
            ## Just insert the organization and return its id
            return self.post_organization(organization)

        updates = {}
        if _retr_organization['state'] == 'deleted':
            ## We need to make it active again!
            updates['state'] = 'active'

        ## todo: Check if we have differences, before updating!

        updated_dict = copy.deepcopy(organization)
        updated_dict.update(updates)

        return self.update_organization(_retr_organization['id'], updated_dict)

    def delete_organization(self, organization_id, ignore_404=True):
        ign404 = SuppressExceptionIf(
            lambda e: ignore_404 and (e.status_code == 404))
        path = '/api/3/action/organization_delete'
        with ign404:
            self.request('PUT', path, data={'id': organization_id})
        path = '/api/3/action/organization_purge'
        with ign404:
            self.request('POST', path, data={'id': organization_id})

    ##============================================================
    ## Licenses
    ##============================================================

    @check_retval(is_list_of(dict))
    def list_licenses(self):
        path = '/api/2/rest/licenses'
        response = self.request('GET', path)
        return response.json()

    ##============================================================
    ## Tags
    ##============================================================

    @check_retval(is_list_of(basestring))
    def list_tags(self):
        path = '/api/2/rest/tag'
        response = self.request('GET', path)
        return response.json()

    @check_retval(is_list_of(dict))
    def list_datasets_with_tag(self, tag_id):
        path = '/api/2/rest/tag/{0}'.format(tag_id)
        response = self.request('GET', path)
        return response.json()

    def iter_datasets_with_tag(self, tag_id):
        for dataset_id in self.list_datasets_with_tag():
            yield self.get_dataset(dataset_id)
