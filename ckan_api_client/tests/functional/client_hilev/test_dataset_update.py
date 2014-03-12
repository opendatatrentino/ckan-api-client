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

    new_dataset = CkanDataset(generate_dataset())
    created = client.create_dataset(new_dataset)

    ##--------------------------------------------------
    ## Try adding a new record

    orig_dataset = client.get_dataset(created.id)
    upd_dataset = copy.deepcopy(orig_dataset)
    upd_dataset.extras['NEW_FIELD_NAME'] = 'NEW_FIELD_VALUE'

    updated = client.update_dataset(upd_dataset)
    assert updated.is_equivalent(client.get_dataset(created.id))
    diffs = diff_mappings(orig_dataset.serialize(), updated.serialize())
    assert diffs['left'] == diffs['right'] == set()
    assert diffs['differing'] == set(['extras'])

    del orig_dataset, upd_dataset, updated, diffs

    ##--------------------------------------------------
    ## Try passing a custom new dict

    orig_dataset = client.get_dataset(created.id)
    upd_dataset = client.get_dataset(created.id)
    # upd_dataset = copy.deepcopy(orig_dataset)
    upd_dataset.extras = dict(
        ('key-{0}'.format(i), 'value-{0}'.format(i))
        for i in xrange(10))

    updated = client.update_dataset(upd_dataset)
    assert updated.is_equivalent(client.get_dataset(created.id))
    diffs = diff_mappings(orig_dataset.serialize(), updated.serialize())
    assert diffs['left'] == diffs['right'] == set()
    assert diffs['differing'] == set(['extras'])

    del orig_dataset, upd_dataset, updated, diffs
