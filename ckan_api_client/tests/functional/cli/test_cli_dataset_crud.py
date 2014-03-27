from ckan_api_client.high_level import CkanHighlevelClient

# import urlparse
# import requests


def test_dataset_import_export(ckan_instance):
    api_key = ckan_instance.get_sysadmin_api_key()

    with ckan_instance.serve():
        client = CkanHighlevelClient(ckan_instance.server_url, api_key=api_key)
        assert client.list_datasets() == []
