#!/bin/bash

cd "$( dirname "$0" )"

export CKAN_VIRTUALENV=$VIRTUAL_ENV
export CKAN_POSTGRES_ADMIN=postgresql://postgres:pass@localhost/postgres
export CKAN_SOLR=http://127.0.0.1:8983/solr

exec python ./run_tests.py
#exec py.test --confcutdir="$PWD" --verbose -rsxX ./tests/
