from ckan_api_client.tests.utils.diff import diff_mappings, diff_sequences


def test_diff_dicts():
    dct1 = {
        'one': 'VAL-1',
        'two': 'VAL-2',
        'three': 'VAL-3',
        'four': 'VAL-4',
        'five': 'VAL-5',
    }
    dct2 = {
        'three': 'VAL-3',
        'four': 'VAL-4-2',
        'five': 'VAL-5-2',
        'six': 'VAL-6',
        'seven': 'VAL-7',
        'eight': 'VAL-8',
    }

    diff = diff_mappings(dct1, dct2)

    assert diff['common'] == set(['three', 'four', 'five'])
    assert diff['left'] == set(['one', 'two'])
    assert diff['right'] == set(['six', 'seven', 'eight'])
    assert diff['differing'] == set(['four', 'five'])


def test_diff_sequences():
    diff = diff_sequences([1, 2, 3], [1, 2, 9])
    assert diff['length_match'] is True
    assert diff['differing'] == set([2])

    diff = diff_sequences([1, 2], [])
    assert diff['length_match'] is False
    assert diff['differing'] == set()

    diff = diff_sequences([0, 0, 0, 0], [0, 1, 0, 1])
    assert diff['length_match'] is True
    assert diff['differing'] == set([1, 3])
