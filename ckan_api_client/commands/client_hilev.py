"""
Commands to query CKan data
"""

import json
import sys

from cliff.lister import Lister

from ckan_api_client.objects import CkanDataset
from .base import CkanCommandBase


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
    """Print a dataset as JSON"""

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
        parser.add_argument('--filename', '-f',
                            help='JSON file from which to read')
        return parser

    def _read_file(self, filename):
        if filename is None or filename == '-':
            return sys.stdin.read()
        with open(filename, 'rb') as f:
            return f.read()

    def take_action(self, parsed_args):
        client = self._get_client(parsed_args)
        raw_data = self._read_file(parsed_args.filename)
        dataset_json = json.loads(raw_data)

        # Load dataset from file
        dataset = CkanDataset(dataset_json)

        # todo: we need to check whether this dataset exists
        #       -> try getting and check..
        dataset.id = None

        dataset.owner_org = None  # todo: fill this
        dataset.groups = []  # todo: fill this

        for resource in dataset.resources:
            resource.id = None

        created = client.create_dataset(dataset)
        self.app.stdout.write(json.dumps(created.serialize()))
