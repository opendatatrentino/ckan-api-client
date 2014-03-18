"""
Command-line utilities for ckan-api-client
"""

import logging
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager


class CkanClientApp(App):
    log = logging.getLogger(__name__)

    def __init__(self):
        super(CkanClientApp, self).__init__(
            description='Ckan API command-line client',
            version='0.1',
            command_manager=CommandManager('ckan_api_client.cli'),
        )


def main(argv=sys.argv[1:]):
    myapp = CkanClientApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
