import copy
import json
import requests
from requests.structures import CaseInsensitiveDict
import urlparse


class CkanClient(object):
    """Simple client for the Ckan API"""

    def __init__(self, url, api_key=None):
        self.url = url
        self.api_key = api_key

    def request(self, method, path, **kw):
        kw = copy.deepcopy(kw)
        if not 'headers' in kw:
            kw['headers'] = CaseInsensitiveDict()
        elif not isinstance(kw['headers'], CaseInsensitiveDict):
            kw['headers'] = CaseInsensitiveDict(kw['headers'])
        if 'data' in kw:
            kw['data'] = json.dumps(kw['data'])
            kw['headers']['Content-type'] = 'application/json'
        if self.api_key is not None:
            kw['headers']['Authorization'] = self.api_key
        url = urlparse.urljoin(self.url, path)
        return requests.request(method, url, **kw)

    def get(self, *a, **kw):
        return self.request('get', *a, **kw)

    def post(self, *a, **kw):
        return self.request('post', *a, **kw)
