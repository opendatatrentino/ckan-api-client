"""
Commands to query CKan data
"""

import json
import logging
import os
import sys

from cliff.lister import Lister

from ckan_api_client.objects import CkanDataset
from ckan_api_client.syncing import SynchronizationClient
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


class ImportDirectory(CkanCommandBase):
    """
    Import data from a directory.
    Data should be organized like this::

        source_dir
        |-- dataset
        |   '-- <json files>
        |-- group
        |   '-- <json files>
        '-- organization
            '-- <json files>
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ImportDirectory, self).get_parser(prog_name)
        parser.add_argument('source_name', nargs=1)
        parser.add_argument('source_dir', nargs=1)
        return parser

    def _load_data(self, source_dir):
        data = {}
        for obj_type in ('dataset', 'group', 'organization'):
            data[obj_type] = {}
            base_dir = os.path.join(source_dir, obj_type)
            for basename in os.listdir(base_dir):
                if basename.startswith('.') or basename.endswith('~'):
                    ## Skip hidden / backup files
                    continue
                filename = os.path.join(base_dir, basename)
                with open(filename, 'rb') as f:
                    obj = json.load(f)
                key = obj['id'] if obj_type == 'dataset' else obj['name']
                data[obj_type][key] = obj
        return data

    def take_action(self, parsed_args):
        client = self._get_client(parsed_args, SynchronizationClient)

        source_name = parsed_args.source_name[0]

        source_dir = parsed_args.source_dir[0]
        if source_dir is None:
            source_dir = os.getcwd()
        source_dir = os.path.abspath(source_dir)

        ## Load data into a big dictionary
        self.log.info("Loading data")
        data = self._load_data(source_dir)

        ## Run syncing and hope for the best!
        self.log.info("Synchronizing data")
        client.sync(source_name, data)
