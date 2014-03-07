# """
# Definitions of object schema
# """

# DATASET_FIELDS = {
#     'core': [
#         'author', 'author_email', 'license_id', 'maintainer',
#         'maintainer_email', 'name', 'notes', 'owner_org', 'private', 'state',
#         'type', 'url'
#     ],
#     'cruft': [
#         'ckan_url', 'creator_user_id', 'isopen', 'license', 'license_title',
#         'license_url', 'metadata_created', 'metadata_modified',
#         'num_resources', 'num_tags', 'organization', 'ratings_average',
#         'ratings_count', 'revision_id', 'version'
#     ],
#     'keys': ['id'],
#     'special': ['extras', 'groups', 'relationships', 'resources'],
# }

# RESOURCE_FIELDS = {
#     'core': [
#         'description', 'format', 'mimetype', 'mimetype_inner', 'name',
#         'position', 'resource_type', 'size', 'url', 'url_type',
#     ],
#     'cruft': [
#         'cache_last_updated', 'cache_url', 'created', 'hash',
# 'last_modified',
#         'package_id', 'resource_group_id', 'webstore_last_updated',
#         'webstore_url',
#     ],
#     'keys': ['id'],
#     'special': [],
# }

# GROUP_FIELDS = {
#     'core': [
#         'approval_status', 'description', 'image_display_url', 'image_url',
#         'is_organization', 'name', 'state', 'title', 'type',
#     ],
#     'cruft': [
#         'created', 'display_name', 'package_count', 'packages',
# 'revision_id',
#     ],
#     'keys': ['id'],
#     'special': ['extras', 'groups', 'tags', 'users'],  # packages?
# }

# ORGANIZATION_FIELDS = GROUP_FIELDS
