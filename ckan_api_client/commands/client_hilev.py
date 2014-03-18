"""
Commands to query CKan data
"""

import json
import os
import sys

from ckan_api_client.high_level import CkanHighlevelClient
from ckan_api_client.objects import CkanDataset

from cliff.command import Command
from cliff.lister import Lister


class CkanCommandBase(Command):
    def get_parser(self, prog_name):
        parser = super(CkanCommandBase, self).get_parser(prog_name)
        parser.add_argument('--url')
        parser.add_argument('--api-key')
        return parser

    def _get_client(self, parsed_args):
        base_url = parsed_args.url
        if base_url is None:
            base_url = os.environ.get('CKAN_URL')
        if base_url is None:
            base_url = 'http://127.0.0.1:5000'

        api_key = parsed_args.api_key
        if api_key is None:
            api_key = os.environ.get('CKAN_API_KEY')

        return CkanHighlevelClient(base_url=base_url, api_key=api_key)


class ListDatasets(CkanCommandBase, Lister):
    """List the IDs of datasets in the Ckan instance"""

    def take_action(self, parsed_args):
        client = self._get_client(parsed_args)
        return (('Id',), ((item,) for item in client.list_datasets()))


class IterDatasets(CkanCommandBase, Lister):
    """
    Prints a table of datasets.
    This might take a long time, as it requires a separate HTTP
    request for each dataset..
    """

    def take_action(self, parsed_args):
        client = self._get_client(parsed_args)

        columns = (
            ('id', lambda x: x.id),
            ('name', lambda x: x.name),
            ('title', lambda x: x.title),
            ('author', lambda x: x.author),
            ('author_email', lambda x: x.author_email),
            ('license_id', lambda x: x.license_id),
            ('maintainer', lambda x: x.maintainer),
            ('maintainer_email', lambda x: x.maintainer_email),
            ('notes', lambda x: x.notes),
            ('owner_org', lambda x: x.owner_org),
            ('private', lambda x: x.private),
            ('state', lambda x: x.state),
            ('type', lambda x: x.type),
            ('url', lambda x: x.url),
            ('extras', lambda x: len(x.extras)),
            ('groups', lambda x: len(x.groups)),
            ('resources', lambda x: len(x.resources)),
        )
        return (
            tuple(x[0] for x in columns),
            (
                tuple(unicode(c[1](ds)).encode('utf-8') for c in columns)
                for ds in client.iter_datasets()
            )
        )


class GetDataset(CkanCommandBase):
    """Import a dataset from JSON file"""

    def get_parser(self, prog_name):
        parser = super(GetDataset, self).get_parser(prog_name)
        parser.add_argument('dataset_id')
        return parser

    def take_action(self, parsed_args):
        client = self._get_client(parsed_args)
        dataset = client.get_dataset(parsed_args.dataset_id)
        self.app.stdout.write(json.dumps(dataset.serialize()))


class ImportDataset(CkanCommandBase):
    """Import a dataset from JSON file"""

    def get_parser(self, prog_name):
        parser = super(ImportDataset, self).get_parser(prog_name)
        parser.add_argument('--filename')
        return parser

    def take_action(self, parsed_args):
        client = self._get_client(parsed_args)

        if parsed_args.filename is None or parsed_args.filename == '-':
            dataset_json = json.load(sys.stdin)
        else:
            with open(parsed_args.filename, 'rb') as fp:
                dataset_json = json.load(fp)

        dataset = CkanDataset(dataset_json)
        # self.app.stdout.write(json.dumps(dataset.serialize()))

        ## todo: we need to check whether this dataset exists
        ##       -> try getting and check..
        dataset.id = None
        dataset.owner_org = None  # todo: fill this
        dataset.groups = []  # todo: fill this
        for resource in dataset.resources:
            resource.id = None
        created = client.create_dataset(dataset)
        self.app.stdout.write(json.dumps(created.serialize()))
