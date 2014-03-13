from ckan_api_client.objects import CkanDataset
from ckan_api_client.tests.utils.generate import generate_dataset


def test_dataset_delete(ckan_client_hl):
    client = ckan_client_hl

    dataset_dict = generate_dataset()
    dataset = CkanDataset(dataset_dict)

    created = client.create_dataset(dataset)
    assert created.is_equivalent(dataset)

    ## Make sure it is in lists
    assert created.id in client.list_datasets()

    ## Delete it
    client.delete_dataset(created.id)
    assert created.id not in client.list_datasets()

    ## Trying to retrieve it again: it would return
    ## a 403 error for anonymous clients and
    ## the dataset with 'state' == 'deleted' for
    ## sysadmins..

    retrieved = client.get_dataset(created.id)
    assert retrieved.state == 'deleted'
