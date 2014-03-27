from ckan_api_client.objects import CkanDataset, CkanGroup, CkanOrganization


def _check_obj(obj_class, obj1, obj2):
    _obj1 = obj_class.from_dict(obj1)
    _obj2 = obj_class.from_dict(obj2)

    # Check in the two ways to check the is_equivalent()
    # implementation..
    assert _obj1.is_equivalent(_obj2)
    assert _obj2.is_equivalent(_obj1)


def check_dataset(dataset, expected):
    return _check_obj(CkanDataset, dataset, expected)


def check_group(group, expected):
    return _check_obj(CkanGroup, group, expected)


def check_organization(organization, expected):
    return _check_obj(CkanOrganization, organization, expected)


def clean_dataset(obj):
    return CkanDataset(obj).serialize()


def clean_group(obj):
    return CkanGroup(obj).serialize()


def clean_organization(obj):
    return CkanOrganization(obj).serialize()
