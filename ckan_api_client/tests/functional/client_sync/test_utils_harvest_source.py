import pytest


@pytest.mark.skipif(True, reason="Disabled")
def test_utils_harvest_source():
    import os
    from .utils.harvest_source import HarvestSource

    here = os.path.abspath(os.path.dirname(__file__))
    data_path = os.path.join(here, os.path.pardir, 'data', 'datitrentino')
    data_path = os.path.realpath(data_path)

    hs = HarvestSource(data_path, 'day-00')
    assert sorted(list(hs)) == ['dataset', 'group', 'organization']

    assert 'dataset' in hs
    assert 'group' in hs
    assert 'organization' in hs

    assert len(hs) == 3

    dataset_count = 0
    for item_id in hs['dataset']:
        assert isinstance(item_id, basestring)
        assert item_id in hs['dataset']
        item = hs['dataset'][item_id]
        assert isinstance(item, dict)
        assert item['id'] == item_id
        dataset_count += 1
    assert len(hs['dataset']) == dataset_count
    assert dataset_count > 0

    organization_count = 0
    for item_id in hs['organization']:
        assert isinstance(item_id, basestring)
        assert item_id in hs['organization']
        item = hs['organization'][item_id]
        assert isinstance(item, dict)
        assert item['id'] == item_id
        organization_count += 1
    assert len(hs['organization']) == organization_count
    assert organization_count > 0

    group_count = 0
    for item_id in hs['group']:
        assert isinstance(item_id, basestring)
        assert item_id in hs['group']
        item = hs['group'][item_id]
        assert isinstance(item, dict)
        assert item['id'] == item_id
        group_count += 1
    assert len(hs['group']) == group_count
    assert group_count > 0
