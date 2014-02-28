#!/bin/bash

# cd "$( dirname "$0" )"
# cd "$( dirname "$0" )/.."

## Use same virtualenv for test tools / client and ckan.
## This is not optimal, but it's a quick way to test both
## against different Python versions
export CKAN_VIRTUALENV=$VIRTUAL_ENV

## Administrative credentials, used by test fixtures
export CKAN_POSTGRES_ADMIN=postgresql://postgres:pass@localhost/postgres
export CKAN_SOLR=http://127.0.0.1:8983/solr

#exec py.test --confcutdir="$PWD" --verbose -rsxX ./tests/
#exec python ./run_tests.py
exec py.test -vvv -rsxX ckan_api_client/tests
