"""Utility functions to validate expectations"""

__all__ = ['check_dataset', 'check_group', 'check_organization']


def _check_obj(obj_class, obj1, obj2):
    _obj1 = obj_class.from_dict(obj1)
    _obj2 = obj_class.from_dict(obj2)

    ## Check in the two ways to check the is_equivalent()
    ## implementation..
    assert _obj1.is_equivalent(_obj2)
    assert _obj2.is_equivalent(_obj1)


def check_dataset(dataset, expected):
    """Make sure ``dataset`` matches the ``expected`` one"""
    from ckan_api_client.objects import CkanDataset
    return _check_obj(CkanDataset, dataset, expected)


def check_group(group, expected):
    """Make sure ``group`` matches the ``expected`` one"""
    from ckan_api_client.objects import CkanGroup
    return _check_obj(CkanGroup, group, expected)


def check_organization(organization, expected):
    """Make sure ``organization`` matches the ``expected`` one"""
    from ckan_api_client.objects import CkanOrganization
    return _check_obj(CkanOrganization, organization, expected)
