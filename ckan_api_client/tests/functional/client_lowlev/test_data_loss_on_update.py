"""
Here we test data loss when updating objects.

In a perfect case, we should just be able to update
things by passing in only the updates, but unfortunately
we need to attach a lot more stuff in order to prevent
them from being deleted.
"""

##----------------------------------------------------------------------
## todo: write test to check updating "groups"
##----------------------------------------------------------------------
## todo: write test to check updating "relationships"
##----------------------------------------------------------------------
## todo: write test to check updating "resources"
##----------------------------------------------------------------------
## todo: check that resources keep the same id upon update
##       - create dataset with some resources
##       - update dataset adding a resource and removing another
##       - check that resources kept the same id based on URL
##       - if not, we have to hack around this.. :(
##----------------------------------------------------------------------

import copy

import pytest

from .utils import ckan_client  # noqa (fixture)
from .utils import prepare_dataset, check_dataset


## Tests for updating datasets
# DATASET_UPDATE_TESTS = [
#     (
#         'just-name-and-title',
#         {'name': 'dataset-1', 'title': 'Dataset #1'},
#         {'title': 'Dataset #1 - new title'},
#         {'name': 'dataset-1', 'title': 'Dataset #1 - new title'}
#     ),
#     (
#         'update-name',
#         {'name': 'dataset-2', 'title': 'Dataset #2'},
#         {'name': 'dataset-2-new'},
#         {'name': 'dataset-2-new', 'title': 'Dataset #2'}
#     ),
# ]

# _DATASET_UPDATE_TESTS_DICT = dict((x[0], x[1:]) for x in DATASET_UPDATE_TESTS)  # noqa


# @pytest.fixture(scope='module', params=[x[0] for x in DATASET_UPDATE_TESTS])
# def dataset_update_case(request):
#     return _DATASET_UPDATE_TESTS_DICT[request.param]


@pytest.mark.xfail(run=False, reason="Requires rewrite of prepare_dataset()")
def test_data_loss_on_update(request, ckan_client):
    """
    Strategy:

    1. We create the dataset
    2. We retrieve the dataset and keep it for later
    3. We send an update
    4. We check that update affected only the desired keys
    """
    our_dataset = prepare_dataset(ckan_client)

    ## Create the dataset
    created_dataset = ckan_client.post_dataset(our_dataset)
    dataset_id = created_dataset['id']
    request.addfinalizer(lambda: ckan_client.delete_dataset(dataset_id))

    ## Make sure that the thing we created makes sense
    retrieved_dataset = ckan_client.get_dataset(dataset_id)
    assert retrieved_dataset == created_dataset
    check_dataset(retrieved_dataset, our_dataset)

    ## Ok, now we can start updating and see what happens..
    updates = {'title': "My new dataset title"}

    expected_updated_dataset = copy.deepcopy(our_dataset)
    expected_updated_dataset.update(updates)

    updated_dataset = ckan_client.update_dataset(dataset_id, updates)
    retrieved_dataset = ckan_client.get_dataset(dataset_id)
    assert updated_dataset == retrieved_dataset

    check_dataset(updated_dataset, expected_updated_dataset)


# def test_dataset_update(request, ckan_client, dataset_update_case):
#     initial, updates, expected = dataset_update_case

#     created = ckan_client.post_dataset(initial)
#     request.addfinalizer(lambda: ckan_client.delete_dataset(created['id']))

#     check_dataset(created, initial)

#     created_r = ckan_client.get_dataset(created['id'])
#     assert created_r == created

#     updated = ckan_client.update_dataset(created['id'], updates)
#     check_dataset(updated, updates)
#     check_dataset(updated, expected)

#     updated_r = ckan_client.get_dataset(created['id'])
#     assert updated_r == updated

#     # todo: we should check differences between created and updated.
#     #       update shouldn't have affected more non-cruft fields than
#     #       the ones specified in the update, which should have been
#     #       set to the expected value.
