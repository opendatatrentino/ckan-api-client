"""
Here we test data loss when updating objects.

In a perfect case, we should just be able to update
things by passing in only the updates, but unfortunately
we need to attach a lot more stuff in order to prevent
them from being deleted.
"""

# ----------------------------------------------------------------------
#  todo: write test to check updating "groups"
# ----------------------------------------------------------------------
#  todo: write test to check updating "relationships"
# ----------------------------------------------------------------------
#  todo: write test to check updating "resources"
# ----------------------------------------------------------------------
#  todo: check that resources keep the same id upon update
#        - create dataset with some resources
#        - update dataset adding a resource and removing another
#        - check that resources kept the same id based on URL
#        - if not, we have to hack around this.. :(
# ----------------------------------------------------------------------

import copy

from .utils import check_dataset, clean_dataset
from ckan_api_client.tests.utils.diff import diff_mappings
from ckan_api_client.tests.utils.generate import generate_dataset


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

    # --------------------------------------------------
    # Create a brand new dataset

    stage_1pre = generate_dataset()
    stage_1 = ckan_client_ll.post_dataset(stage_1pre)
    dataset_id = stage_1['id']
    check_dataset(stage_1pre, stage_1)

    # --------------------------------------------------
    # Make sure that the thing we created makes sense

    retrieved = ckan_client_ll.get_dataset(dataset_id)
    assert retrieved == stage_1
    check_dataset(stage_1pre, stage_1)

    # --------------------------------------------------
    # Try updating, then double-check

    stage_2pre = copy.deepcopy(retrieved)
    stage_2pre['title'] = 'My new dataset title'

    stage_2 = ckan_client_ll.put_dataset(stage_2pre)
    assert stage_2['title'] == 'My new dataset title'

    # Compare with previous stage
    diffs = diff_mappings(*map(clean_dataset, (stage_1, stage_2)))
    assert diffs['right'] == diffs['left'] == set()
    assert diffs['differing'] == set(['title'])

    check_dataset(stage_2pre, stage_2)
