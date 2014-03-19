import os

from ckan_api_client.high_level import CkanHighlevelClient

from cliff.command import Command


class CkanCommandBase(Command):
    def get_parser(self, prog_name):
        parser = super(CkanCommandBase, self).get_parser(prog_name)
        parser.add_argument('--url')
        parser.add_argument('--api-key')
        return parser

    def _get_client(self, parsed_args, klass=CkanHighlevelClient):
        base_url = parsed_args.url
        if base_url is None:
            base_url = os.environ.get('CKAN_URL')
        if base_url is None:
            base_url = 'http://127.0.0.1:5000'

        api_key = parsed_args.api_key
        if api_key is None:
            api_key = os.environ.get('CKAN_API_KEY')

        return klass(base_url=base_url, api_key=api_key)
