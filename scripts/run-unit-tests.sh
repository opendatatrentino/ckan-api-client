#!/bin/sh
exec py.test -vvv -rsxX --pep8 \
     --cov-report=term-missing --cov=ckan_api_client \
     ckan_api_client/tests/unit "$@"
