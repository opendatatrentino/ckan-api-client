"""
Commands to query CKan data
"""

import json
import logging
import os
import sqlite3

from ckan_api_client.syncing import SynchronizationClient
from .base import CkanCommandBase


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
                    # Skip hidden / backup files
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

        # Load data into a big dictionary
        self.log.info("Loading data")
        data = self._load_data(source_dir)

        # Run syncing and hope for the best!
        self.log.info("Synchronizing data")
        client.sync(source_name, data)


class ImportSQLite(CkanCommandBase):
    """
    Import data from a SQLite database.

    The database is basically a key/value store.

    Each table has two columns:

    - ``id`` can be INT or VARCHAR
    - ``json_data`` is TEXT containing a JSON-serialized object
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ImportSQLite, self).get_parser(prog_name)
        parser.add_argument('source_name', nargs=1)
        parser.add_argument('sqlite_file', nargs=1)
        parser.add_argument('--dataset-table', default='dataset')
        parser.add_argument('--group-table', default='group')
        parser.add_argument('--organization-table', default='organization')
        return parser

    def _load_from_table(self, db, table):
        query = 'SELECT * FROM "{0}";'.format(table)
        cur = db.cursor()
        cur.execute(query)
        data = {}
        for row in cur.fetchall():
            obj = json.loads(row['json_data'])
            data[str(row['id'])] = obj
        return data

    def take_action(self, parsed_args):
        client = self._get_client(parsed_args, SynchronizationClient)

        sqlite_db = sqlite3.connect(parsed_args.sqlite_file[0])
        sqlite_db.row_factory = sqlite3.Row

        self.log.info("Loading data from SQLite db")
        data = {
            'dataset': self._load_from_table(
                sqlite_db, parsed_args.dataset_table),
            'group': self._load_from_table(
                sqlite_db, parsed_args.group_table),
            'organization': self._load_from_table(
                sqlite_db, parsed_args.organization_table),
        }

        self.log.info("Synchronizing data")
        client.sync(parsed_args.source_name[0], data)
