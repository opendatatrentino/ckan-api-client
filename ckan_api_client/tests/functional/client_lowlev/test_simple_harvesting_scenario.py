# """
# Test some simple harvesting scenarios
# """

# import os

# import pytest

# from ckan_api_client.syncing import CkanDataImportClient
# from .utils.harvest_source import HarvestSource


# HERE = os.path.abspath(os.path.dirname(__file__))
# DATA_DIR = os.path.join(os.path.dirname(HERE), 'data', 'random')

# HARVEST_SOURCE_NAME = 'dummy-harvest-source'


# @pytest.fixture(params=['day-{0:02d}'.format(x) for x in xrange(4)])
# def harvest_source(request):
#     return HarvestSource(DATA_DIR, request.param)
