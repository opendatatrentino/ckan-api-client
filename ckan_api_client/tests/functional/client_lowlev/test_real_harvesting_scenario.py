# """
# Test some "real life" harvesting scenario.

# We have "data dumps" of an imaginary catalog for a set of days.

# The testing procedure should be run as follows:

# 1- Get current state of the database
# 2- Update data from the "harvest source"
# 3- Make sure the database state matches the expected one:
#    - unrelated datasets should still be there
#    - only datasets from this souce should have been changed,
#      and should match the desired state.
# 4- Loop for all the days
# """

# import os

# import pytest

# from ckan_api_client.syncing import CkanDataImportClient
# from .utils import ckan_client  # noqa (fixture)
# # from .utils.harvest_source import HarvestSource


# HERE = os.path.abspath(os.path.dirname(__file__))
# DATA_DIR = os.path.join(os.path.dirname(HERE), 'data', 'random')

# HARVEST_SOURCE_NAME = 'dummy-harvest-source'


# @pytest.fixture(params=['day-{0:02d}'.format(x) for x in xrange(4)])
# def harvest_source(request):
#     return HarvestSource(DATA_DIR, request.param)


# @pytest.mark.skipif(True, reason="Disabled")
# def test_real_harvesting_scenario(ckan_url, api_key, harvest_source):
#     client = CkanDataImportClient(ckan_url, api_key, 'test-source')
#     client.sync_data(harvest_source, double_check=True)
