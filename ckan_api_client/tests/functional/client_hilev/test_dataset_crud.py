import copy

import pytest

from ckan_api_client.exceptions import HTTPError
from ckan_api_client.objects import CkanDataset
from ckan_api_client.tests.utils.diff import diff_mappings
from ckan_api_client.tests.utils.generate import generate_dataset
from ckan_api_client.tests.utils.validation import MutableCheckpoint


def test_dataset_create(ckan_client_hl):
    client = ckan_client_hl
    dataset_dict = generate_dataset()
    dataset = CkanDataset(dataset_dict)
    created = client.create_dataset(dataset)
    assert created.is_equivalent(dataset)


def test_dataset_get_by_name(ckan_client_hl):
    client = ckan_client_hl
    dataset_dict = generate_dataset()
    dataset_dict['name'] = 'example-dataset-name'
    dataset = CkanDataset(dataset_dict)
    created = client.create_dataset(dataset)
    assert created.is_equivalent(dataset)
    dataset_id = created.id

    # Try getting by id
    dataset_1 = client.get_dataset(dataset_id)
    assert created == dataset_1

    # Try getting by name
    dataset_2 = client.get_dataset_by_name('example-dataset-name')
    assert created == dataset_2

    # Try getting by id, but passing name instead
    with pytest.raises(HTTPError) as excinfo:
        client.get_dataset('example-dataset-name')
    assert excinfo.value.status_code == 404

    # Try getting by name, but passing id instead
    with pytest.raises(HTTPError) as excinfo:
        client.get_dataset_by_name(dataset_id)
    assert excinfo.value.status_code == 404


def test_dataset_update_base_fields(ckan_client_hl):
    client = ckan_client_hl  # shortcut
    ckp = MutableCheckpoint()  # to check objects mutation

    # Create our dataset
    dataset_dict = generate_dataset()
    ckp.add(dataset_dict)

    dataset = CkanDataset(generate_dataset())
    dataset.author = 'original author'
    dataset.author_email = 'original.author@example.com'
    dataset.license_id = 'cc-zero'
    created = client.create_dataset(dataset)

    # Store a copy of the original dataset
    original_dataset = client.get_dataset(created.id)
    assert created.is_equivalent(original_dataset)
    ckp.add(original_dataset)

    # Update some base fields, send back & check
    to_be_updated = copy.deepcopy(original_dataset)
    to_be_updated.author = 'NEW_AUTHOR'
    to_be_updated.author_email = 'NEW_AUTHOR_EMAIL'
    to_be_updated.license_id = 'cc-by-sa'
    assert to_be_updated.is_modified()

    # Update, get back, check
    updated = client.update_dataset(to_be_updated)
    updated_2 = client.get_dataset(created.id)

    assert updated.is_equivalent(to_be_updated)
    assert updated.is_equivalent(updated_2)

    diffs = diff_mappings(
        original_dataset.serialize(),
        updated.serialize())
    assert diffs['differing'] == set([
        'author', 'author_email', 'license_id',
    ])
    assert diffs['left'] == set()
    assert diffs['right'] == set()

    # Make sure dicts did not mutate
    ckp.check()


def test_dataset_update_extras(ckan_client_hl):
    client = ckan_client_hl  # shortcut

    ds_dict = generate_dataset()
    ds_dict['extras'] = {
        'key-0': 'value-0',
        'key-1': 'value-1',
        'key-2': 'value-2',
        'key-3': 'value-3',
        'key-4': 'value-4',
        'key-5': 'value-5',
        'key-6': 'value-6',
        'key-7': 'value-7',
        'key-8': 'value-8',
        'key-9': 'value-9',
    }
    stage_1pre = CkanDataset(ds_dict)
    stage_1 = client.create_dataset(stage_1pre)

    # --------------------------------------------------
    # Try adding a new record

    stage_1b = client.get_dataset(stage_1.id)
    stage_2pre = copy.deepcopy(stage_1b)
    stage_2pre.extras['NEW_FIELD_NAME'] = 'NEW_FIELD_VALUE'

    stage_2 = client.update_dataset(stage_2pre)
    assert stage_2.is_equivalent(client.get_dataset(stage_1.id))
    diffs = diff_mappings(stage_1b.serialize(), stage_2.serialize())
    assert diffs['left'] == diffs['right'] == set()
    assert diffs['differing'] == set(['extras'])

    del stage_1b, stage_2pre, stage_2, diffs

    # --------------------------------------------------
    # Try removing the custom field

    stage_2pre = client.get_dataset(stage_1.id)
    del stage_2pre.extras['NEW_FIELD_NAME']

    stage_2 = client.update_dataset(stage_2pre)
    assert stage_2.is_equivalent(client.get_dataset(stage_1.id))
    assert 'NEW_FIELD_NAME' not in stage_2.extras
    stage_2b = client.get_dataset(stage_1.id)
    assert stage_2 == stage_2b

    # Make sure we brought it back to its original state
    assert stage_1.is_equivalent(stage_2)

    del stage_2pre, stage_2


def test_dataset_update_resources(ckan_client_hl):
    client = ckan_client_hl  # shortcut

    ds_dict = generate_dataset()
    ds_dict['resources'] = [
        {'name': 'example-csv-1',
         'url': 'http://example.com/dataset-1.csv',
         'format': 'CSV'},
        {'name': 'example-json-1',
         'url': 'http://example.com/dataset-1.json',
         'format': 'JSON'},
    ]
    stage_1pre = CkanDataset(ds_dict)
    stage_1 = client.create_dataset(stage_1pre)

    # --------------------------------------------------
    # Try adding a new resource

    stage_2pre = client.get_dataset(stage_1.id)
    stage_2pre.resources.append({
        'name': 'example-csv-2',
        'url': 'http://example.com/dataset-2.csv',
        'format': 'CSV'})

    assert len(stage_2pre.resources) == 3
    assert len(stage_2pre.serialize()['resources']) == 3

    stage_2 = client.update_dataset(stage_2pre)
    assert len(stage_2.resources) == 3
    assert len(stage_2.serialize()['resources']) == 3

    # --------------------------------------------------
    # Try prepending adding a new resource

    stage_3pre = client.get_dataset(stage_1.id)
    stage_3pre.resources.insert(0, {
        'url': 'http://example.com/dataset-2.json',
        'format': 'JSON'})

    assert len(stage_3pre.resources) == 4
    assert len(stage_3pre.serialize()['resources']) == 4

    stage_3 = client.update_dataset(stage_3pre)
    assert len(stage_3.resources) == 4
    assert len(stage_3.serialize()['resources']) == 4


def test_dataset_delete(ckan_client_hl):
    client = ckan_client_hl

    dataset_dict = generate_dataset()
    dataset = CkanDataset(dataset_dict)

    created = client.create_dataset(dataset)
    assert created.is_equivalent(dataset)

    # Make sure it is in lists
    assert created.id in client.list_datasets()

    # Delete it
    client.delete_dataset(created.id)
    assert created.id not in client.list_datasets()

    # Test that our workarounds work as expected..

    with pytest.raises(HTTPError) as excinfo:
        client.get_dataset(created.id)
    assert excinfo.value.status_code == 404

    retrieved = client.get_dataset(created.id, allow_deleted=True)
    assert retrieved.state == 'deleted'


def test_dataset_wipe(ckan_client_hl):
    client = ckan_client_hl

    # ------------------------------------------------------------
    # Now delete normally and try inserting another
    # one with the same name. Should fail with 409

    dataset = CkanDataset(generate_dataset())
    dataset.name = 'dataset-to-delete'

    created = client.create_dataset(dataset)
    assert created.is_equivalent(dataset)

    client.delete_dataset(created.id)

    new_dataset = CkanDataset(generate_dataset())
    new_dataset.name = 'dataset-to-delete'

    with pytest.raises(HTTPError) as excinfo:
        client.create_dataset(new_dataset)
    assert excinfo.value.status_code == 409

    del dataset, created, new_dataset, excinfo

    # ------------------------------------------------------------
    # Now let's try updating + deleting

    dataset = CkanDataset(generate_dataset())
    dataset.name = 'dataset-to-delete-2'

    created = client.create_dataset(dataset)
    assert created.is_equivalent(dataset)

    client.wipe_dataset(created.id)

    new_dataset = CkanDataset(generate_dataset())
    new_dataset.name = 'dataset-to-delete-2'

    # Should not fail anymore
    created = client.create_dataset(new_dataset)
    assert created.name == 'dataset-to-delete-2'
