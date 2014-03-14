"""
Test some simple harvesting scenarios, generating data on-the-fly
"""

# import os
import random

# import pytest

# from ckan_api_client.syncing import CkanDataImportClient
# from .utils.harvest_source import HarvestSource
from ckan_api_client.tests.utils.generate import (
    generate_organization, generate_group, generate_dataset)


def generate_data():
    organizations = {}
    groups = {}
    datasets = {}

    for i in xrange(3):
        org = generate_organization()
        org['id'] = org['name'] = 'org-{0}'.format(i)
        organizations[org['name']] = org

    for i in xrange(10):
        grp = generate_group()
        grp['id'] = grp['name'] = 'group-{0}'.format(i)
        groups[grp['id']] = grp

    for i in xrange(20):
        dataset = generate_dataset()
        dataset['id'] = 'dataset-{0}'.format(i)
        dataset['groups'] = random.sample(list(groups), random.randint(0, 3))
        dataset['owner_org'] = random.choice(list(organizations))
        datasets[dataset['id']] = dataset

    return {
        'organization': organizations,
        'group': groups,
        'dataset': datasets,
    }


def test_simple_harvesting(ckan_client_sync):
    client = ckan_client_sync
    data = generate_data()

    client.sync('dummy-source', data)
