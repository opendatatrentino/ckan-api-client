"""
Utilities to figure out differences between objects
"""


def diff_mappings(left, right):
    """
    Compares two mappings, returning a dictionary of
    sets of keys describing differences.

    Dictionary keys are as follows:

    - ``common`` -- keys in both mappings
    - ``differing`` -- keys that are in both mappings, but
      whose values differ
    - ``left`` -- keys only in the "left" object
    - ``right`` -- keys only in the "right" object

    :param dict-like left: "left" object to compare
    :param dict-like right: "right" object to compare
    :rtype: dict
    """

    left_keys = set(left.iterkeys())
    right_keys = set(right.iterkeys())

    common_keys = left_keys & right_keys
    left_only_keys = left_keys - right_keys
    right_only_keys = right_keys - left_keys

    differing = set(k for k in common_keys if left[k] != right[k])

    return {
        'common': common_keys,
        'left': left_only_keys,
        'right': right_only_keys,
        'differing': differing,
    }


def diff_sequences(left, right):
    """
    Compare two sequences, return a dict containing differences
    """

    return {
        'length_match': len(left) == len(right),
        'differing': set([
            i for i, (l, r) in enumerate(zip(left, right))
            if l != r
        ])}
