#!/bin/sh
exec py.test -vvv -rsxX ckan_api_client/tests/unit "$@"
