import copy

from ckan_api_client.objects import CkanDataset
from ckan_api_client.tests.utils.generate import generate_dataset
from ckan_api_client.tests.utils.validation import MutableCheckpoint
from ckan_api_client.tests.utils.diff import diff_mappings


def test_dataset_update_base_fields(ckan_client_hl):
    client = ckan_client_hl  # shortcut
    ckp = MutableCheckpoint()  # to check objects mutation

    ## Create our dataset
    dataset_dict = generate_dataset()
    ckp.add(dataset_dict)

    dataset = CkanDataset(generate_dataset())
    dataset.author = 'original author'
    dataset.author_email = 'original.author@example.com'
    dataset.license_id = 'cc-zero'
    created = client.create_dataset(dataset)

    ## Store a copy of the original dataset
    original_dataset = client.get_dataset(created.id)
    assert created.is_equivalent(original_dataset)
    ckp.add(original_dataset)

    ## Update some base fields, send back & check
    to_be_updated = copy.deepcopy(original_dataset)
    to_be_updated.author = 'NEW_AUTHOR'
    to_be_updated.author_email = 'NEW_AUTHOR_EMAIL'
    to_be_updated.license_id = 'cc-by-sa'
    assert to_be_updated.is_modified()

    ## Update, get back, check
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

    ## Make sure dicts did not mutate
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

    ##--------------------------------------------------
    ## Try adding a new record

    stage_1b = client.get_dataset(stage_1.id)
    stage_2pre = copy.deepcopy(stage_1b)
    stage_2pre.extras['NEW_FIELD_NAME'] = 'NEW_FIELD_VALUE'

    stage_2 = client.update_dataset(stage_2pre)
    assert stage_2.is_equivalent(client.get_dataset(stage_1.id))
    diffs = diff_mappings(stage_1b.serialize(), stage_2.serialize())
    assert diffs['left'] == diffs['right'] == set()
    assert diffs['differing'] == set(['extras'])

    del stage_1b, stage_2pre, stage_2, diffs

    ##--------------------------------------------------
    ## Try removing the custom field

    stage_2pre = client.get_dataset(stage_1.id)
    del stage_2pre.extras['NEW_FIELD_NAME']

    stage_2 = client.update_dataset(stage_2pre)
    assert stage_2.is_equivalent(client.get_dataset(stage_1.id))
    assert 'NEW_FIELD_NAME' not in stage_2.extras
    stage_2b = client.get_dataset(stage_1.id)
    assert stage_2 == stage_2b

    ## Make sure we brought it back to its original state
    assert stage_1.is_equivalent(stage_2)

    del stage_2pre, stage_2
