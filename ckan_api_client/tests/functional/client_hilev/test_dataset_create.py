from ckan_api_client.objects import CkanDataset
from ckan_api_client.tests.utils.generate import generate_dataset


def test_dataset_create(ckan_client_hl):
    client = ckan_client_hl
    dataset_dict = generate_dataset()
    dataset = CkanDataset(dataset_dict)
    created = client.create_dataset(dataset)
    assert created.is_equivalent(dataset)
