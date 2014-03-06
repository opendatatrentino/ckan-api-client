"""
Download data from a Ckan website to a given directory
"""

import json
import os
import sys
import urlparse

import requests


class HTTPError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return "HTTPError [{0}]: {1}".format(self.status_code, self.message)


class CkanReadClient(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def request(self, method, path, **kwargs):
        headers = kwargs.get('headers') or {}
        kwargs['headers'] = headers

        if isinstance(path, (list, tuple)):
            path = '/'.join(path)

        path = path.strip('/')

        url = urlparse.urljoin(self.base_url, path)
        response = requests.request(method, url, **kwargs)
        if not response.ok:
            ## todo: attach message, if any available..
            raise HTTPError(response.status_code,
                            "Error while performing request")

        return response

    def list_datasets(self):
        path = '/api/2/rest/dataset'
        response = self.request('GET', path)
        return response.json()

    def iter_datasets(self):
        for ds_id in self.list_datasets():
            yield self.get_dataset(ds_id)

    def get_dataset(self, dataset_id):
        path = '/api/2/rest/dataset/{0}'.format(dataset_id)
        response = self.request('GET', path)
        return response.json()

    def list_groups(self):
        path = '/api/2/rest/group'
        response = self.request('GET', path)
        return response.json()

    def iter_groups(self):
        all_groups = self.list_groups()
        for group_id in all_groups:
            yield self.get_group(group_id)

    def get_group(self, group_id):
        path = '/api/2/rest/group/{0}'.format(group_id)
        response = self.request('GET', path)
        return response.json()

    def list_organizations(self):
        path = '/api/3/action/organization_list'
        response = self.request('GET', path)
        return response.json()['result']

    def iter_organizations(self):
        for org_id in self.list_organizations():
            yield self.get_organization(org_id)

    def get_organization(self, organization_id):
        path = '/api/3/action/organization_show?id={0}'.format(organization_id)
        response = self.request('GET', path)
        return response.json()['result']

    def list_tags(self):
        path = '/api/2/rest/tag'
        response = self.request('GET', path)
        return response.json()

    def iter_tags(self):
        for ds_id in self.list_tags():
            yield self.get_tag(ds_id)

    def get_tag(self, tag_id):
        path = '/api/2/rest/tag/{0}'.format(tag_id)
        response = self.request('GET', path)
        return response.json()


if __name__ == '__main__':
    try:
        base_url = sys.argv[1]
        dest_dir = sys.argv[2]
    except IndexError:
        print("Usage: download_ckan_data.py <base_url> <dest_dir>")
        sys.exit(1)

    client = CkanReadClient(base_url)

    if os.path.exists(dest_dir):
        raise ValueError("Destination directory already exists")

    os.makedirs(dest_dir)
    os.makedirs(os.path.join(dest_dir, 'dataset'))
    os.makedirs(os.path.join(dest_dir, 'group'))
    os.makedirs(os.path.join(dest_dir, 'organization'))
    os.makedirs(os.path.join(dest_dir, 'tag'))

    print("\033[1;36mDownloading datasets\033[0m")
    for obj in client.iter_datasets():
        print("\033[0;36mDownloaded object: {0}\033[0m".format(obj['id']))
        destfile = os.path.join(dest_dir, 'dataset', obj['id'])
        with open(destfile, 'w') as f:
            f.write(json.dumps(obj))

    print("\033[1;36mDownloading groups\033[0m")
    for obj in client.iter_groups():
        print("\033[0;36mDownloaded object: {0}\033[0m".format(obj['id']))
        destfile = os.path.join(dest_dir, 'group', obj['id'])
        with open(destfile, 'w') as f:
            f.write(json.dumps(obj))

    print("\033[1;36mDownloading organizations\033[0m")
    for obj in client.iter_organizations():
        print("\033[0;36mDownloaded object: {0}\033[0m".format(obj['id']))
        destfile = os.path.join(dest_dir, 'organization', obj['id'])
        with open(destfile, 'w') as f:
            f.write(json.dumps(obj))

    # print("\033[1;36mDownloading tags\033[0m")
    # for obj in client.iter_tags():
    #     print("\033[0;36mDownloaded object: {0}\033[0m".format(obj['id']))
    #     destfile = os.path.join(dest_dir, 'tag', obj['id'])
    #     with open(destfile, 'w') as f:
    #         f.write(json.dumps(obj))
