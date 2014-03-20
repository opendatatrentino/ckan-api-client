# Importing data from statistica


## Downloading data

Use: https://github.com/opendatatrentino/data-crawlers

```shell
cd data-crawlers/statistica
./download_statistica_140320.py
```

From the interactive prompt:


```python
app = App()
app.download_raw_data()
app.cleanup_data()
```

## Importing data

Use: https://github.com/rshk/ckan-api-client

```shell
export CKAN_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
export CKAN_URL=http://127.0.0.1:5000
export DATA_SQLITE_FILE=..../data-crawlers/statistica/.statistica-140320-clean.sqlite
```

Run import scripts on the previously generated SQLite file:

```shell
ckanclient -vvv import sqlite statistica-prov "$DATA_SQLITE_FILE" --dataset-table dataset_statistica
ckanclient -vvv import sqlite statistica-subpro "$DATA_SQLITE_FILE" --dataset-table dataset_statistica_subpro
```

To run under debugger:

```shell
ipdb $( which ckanclient ) --debug -vvv import sqlite statistica-prov "$DATA_SQLITE_FILE" \
    --dataset-table dataset_statistica
ipdb $( which ckanclient ) --debug -vvv import sqlite statistica-subpro "$DATA_SQLITE_FILE" \
    --dataset-table dataset_statistica_subpro
```
