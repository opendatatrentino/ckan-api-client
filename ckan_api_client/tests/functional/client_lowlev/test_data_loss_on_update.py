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

from .utils import check_dataset
from ckan_api_client.tests.utils.generate import generate_dataset


@pytest.mark.xfail(run=False, reason="Requires rewrite of prepare_dataset()")
def test_data_loss_on_update(request, ckan_client_ll):
    """
    Check whether / which data gets lost if not passed back
    with the object during an update.

    Strategy:

    1. We create the dataset
    2. We retrieve the dataset and keep it for later
    3. We send an update
    4. We check that update affected only the desired keys
    """

    # our_dataset = prepare_dataset(ckan_client_ll)
    our_dataset = generate_dataset()

    ## Create the dataset
    created_dataset = ckan_client_ll.post_dataset(our_dataset)
    dataset_id = created_dataset['id']
    request.addfinalizer(lambda: ckan_client_ll.delete_dataset(dataset_id))

    ## Make sure that the thing we created makes sense
    retrieved_dataset = ckan_client_ll.get_dataset(dataset_id)
    assert retrieved_dataset == created_dataset
    check_dataset(retrieved_dataset, our_dataset)

    ## Ok, now we can start updating and see what happens..
    updates = {'title': "My new dataset title"}

    expected_updated_dataset = copy.deepcopy(our_dataset)
    expected_updated_dataset.update(updates)

    updated_dataset = ckan_client_ll.update_dataset(dataset_id, updates)
    retrieved_dataset = ckan_client_ll.get_dataset(dataset_id)
    assert updated_dataset == retrieved_dataset

    check_dataset(updated_dataset, expected_updated_dataset)

    ## todo: now do the same with other fields (groups, extras, ..)
