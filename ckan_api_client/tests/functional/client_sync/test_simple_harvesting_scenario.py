"""
Test some simple harvesting scenarios, generating data on-the-fly
"""

# import os
import random

# import pytest

# from ckan_api_client.syncing import CkanDataImportClient
# from .utils.harvest_source import HarvestSource
from ckan_api_client.tests.utils.generate import (
    generate_organization, generate_group, generate_dataset, generate_id)


def generate_data():
    organizations = generate_organizations(5)
    groups = generate_groups(10)

    datasets = generate_datasets(
        groups=groups, organizations=organizations, amount=20)

    return {
        'organization': organizations,
        'group': groups,
        'dataset': datasets,
    }


def generate_organizations(amount=10):
    organizations = {}
    for i in xrange(3):
        org = generate_organization()
        org['id'] = org['name'] = 'org-{0}'.format(generate_id())
        organizations[org['name']] = org
    return organizations


def generate_groups(amount=10):
    groups = {}
    for i in xrange(10):
        grp = generate_group()
        grp['id'] = grp['name'] = 'group-{0}'.format(generate_id())
        groups[grp['id']] = grp
    return groups


def generate_datasets(groups, organizations, amount=20):
    datasets = {}
    for i in xrange(amount):
        dataset = generate_dataset()
        dataset['id'] = 'dataset-{0}'.format(generate_id())
        dataset['groups'] = random.sample(list(groups), random.randint(0, 3))
        dataset['owner_org'] = random.choice(list(organizations))
        datasets[dataset['id']] = dataset
    return datasets


def test_simple_harvesting(ckan_client_sync):
    client = ckan_client_sync

    # ------------------------------------------------------------
    # Initial import of data

    data = generate_data()
    assert len(data['dataset']) == 20

    client.sync('dummy-source', data)
    #  todo: check current status

    # ------------------------------------------------------------
    #  Add 20 new datasets

    new_datasets = generate_datasets(
        groups=data['group'],
        organizations=data['organization'],
        amount=20)

    data['dataset'].update(new_datasets)
    assert len(data['dataset']) == 40

    client.sync('dummy-source', data)
    #  todo: check current status

    # ------------------------------------------------------------
    #  Randomly remove 15 datasets, add 20

    todel = random.sample(data['dataset'].keys(), 15)
    for key in todel:
        del data['dataset'][key]

    new_datasets = generate_datasets(
        groups=data['group'],
        organizations=data['organization'],
        amount=20)
    data['dataset'].update(new_datasets)
    assert len(data['dataset']) == 45

    client.sync('dummy-source', data)
    #  todo: check current status

    # ------------------------------------------------------------
    #  Datasets: -25 +50 (should be 80 now..)
    #  Organizations: +10
    #  Groups: +20
    # ------------------------------------------------------------

    todel = random.sample(data['dataset'].keys(), 25)
    for key in todel:
        del data['dataset'][key]

    data['group'].update(generate_groups(20))
    data['organization'].update(generate_organizations(10))

    new_datasets = generate_datasets(
        groups=data['group'],
        organizations=data['organization'],
        amount=20)
    data['dataset'].update(new_datasets)

    client.sync('dummy-source', data)
    #  todo: check current status

    # ------------------------------------------------------------
    #  Now the tricky thing: we need to apply random
    #  changes to objects and make sure they are updated
    #  correctly..
