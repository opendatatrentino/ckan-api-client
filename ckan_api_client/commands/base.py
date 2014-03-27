import os
import csv
from collections import namedtuple

from cliff.command import Command

from ckan_api_client.high_level import CkanHighlevelClient


class PasswdDialect(csv.Dialect):
    delimiter = ':'
    doublequote = False  # means: use escapechar to escape quotechar
    escapechar = '\\'
    lineterminator = os.linesep
    quotechar = '\x00'
    quoting = csv.QUOTE_NONE
    skipinitialspace = False


passwd_row = namedtuple('passwd_row', 'url,api_key')


class CkanCommandBase(Command):
    """Base for commands that need configuration for a Ckan instance"""

    def get_parser(self, prog_name):
        parser = super(CkanCommandBase, self).get_parser(prog_name)
        parser.add_argument('--url')
        parser.add_argument('--api-key')
        return parser

    def _get_base_url(self):
        if 'CKAN_URL' in os.environ:
            return os.environ['CKAN_URL']
        return 'http://127.0.0.1:5000'

    def _get_api_key(self):
        os.environ.get('CKAN_API_KEY')
        if 'CKAN_API_KEY' in os.environ:
            return os.environ['CKAN_API_KEY']

    def _iter_passwd_file(self):
        PASSWORD_FILE = os.path.expanduser('~/.ckanpass')
        with open(PASSWORD_FILE, 'r') as fp:
            csvr = csv.reader(fp, dialect=PasswdDialect())
            for _row in csvr:
                yield passwd_row(*_row)

    def _find_api_key(self, base_url):
        for row in self._iter_passwd_file():
            if row.url == base_url:
                return row.api_key

    def _get_client(self, parsed_args, klass=CkanHighlevelClient):
        base_url = parsed_args.url
        if base_url is None:
            base_url = self._get_base_url()

        api_key = parsed_args.api_key
        if api_key is None:
            api_key = self._find_api_key(base_url)
        if api_key is None:
            api_key = self._get_api_key()

        return klass(base_url=base_url, api_key=api_key)
