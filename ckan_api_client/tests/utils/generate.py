#!/usr/bin/env python

# Generate some dummy data, for testing purposes

import json
import random
import string

from .strings import gen_random_id, gen_picture


def generate_organization():
    """
    Generate a random organization object, with:

    - ``name``, random, example: ``"org-abc123"``
    - ``title``, random, example: ``"Organization abc123"``
    - ``description``, random
    - ``image``, url pointing to a random-generated pic
    """

    random_id = gen_random_id(10)
    return {
        "name": "org-{0}".format(random_id),  # Used as key
        "title": "Organization {0}".format(random_id),
        "description": "Description of organization {0}".format(random_id),
        "image_url": gen_picture(random_id),
        # "extras": [],
        # "tags": [],
    }


def generate_group():
    """
    Generate a random group object, with:

    - ``name``, random, example: ``"grp-abc123"``
    - ``title``, random, example: ``"Group abc123"``
    - ``description``, random
    - ``image``, url pointing to a random-generated pic
    """

    random_id = gen_random_id(10)
    return {
        "name": "grp-{0}".format(random_id),  # Used as key
        "title": "Group {0}".format(random_id),
        "description": "Description of group {0}".format(random_id),
        "image_url": gen_picture(random_id),
        # "extras": [],
        # "tags": [],
    }


def generate_dataset():
    """
    Generate a dataset, populated with random data.

    **Fields:**

    - ``name`` -- random string, in the form ``dataset-{random}``
    - ``title`` -- random string, in the form ``Dataset {random}``

    - ``author`` -- random-generated name
    - ``author_email`` -- random-generated email address
    - ``license_id`` -- random license id. One of ``cc-by``, ``cc-zero``,
      ``cc-by-sa`` or ``notspecified``.
    - ``maintainer`` -- random-generated name
    - ``maintainer_email`` -- random-generated email address
    - ``notes`` -- random string, containing some markdown
    - ``owner_org`` -- set to None
    - ``private`` -- Fixed to ``False``
    - ``tags`` -- random list of tags (strings)
    - ``type`` -- fixed string: ``"dataset"``
    - ``url`` -- random url of dataset on an "external source"

    - ``extras`` -- dictionary containing random key / value pairs
    - ``groups`` -- empty list
    - ``resources`` -- list of random resources
    - ``relationships`` -- empty list

    .. note::
        The ``owner_org`` and ``groups`` fields will be blank,
        as they must match with existing groups / organizations
        and we don't have access to database from here (nor
        is it in the scope of this function!)
    """

    random_id = gen_random_id(15)
    license_id = random.choice((
        'cc-by', 'cc-zero', 'cc-by-sa', 'notspecified'))
    resources = []
    for i in xrange(random.randint(1, 8)):
        resources.append(generate_resource())
    return {
        # ------------------------------------------------------------
        # WARNING! This is the **internal** id of the external
        # service, which will need to be moved to
        # dataset['extras']['_harvest_source_id']
        # ------------------------------------------------------------
        # "id": random_id,

        # Name should be taken as a "suggestion": in case of naming conflict
        # with an existing dataset, it just be changed (todo: how?)
        "name": "dataset-{0}".format(random_id),

        "title": "Dataset {0}".format(random_id),
        "url": "http://www.example.com/dataset/{0}".format(random_id),
        "type": "dataset",

        "maintainer_email": "maintainer-{0}@example.com".format(random_id),
        "maintainer": "Maintainer {0}".format(random_id),

        "author_email": "author-{0}@example.com".format(random_id),
        "author": "Author {0}".format(random_id),

        "license_id": license_id,

        "private": False,
        "notes": "Notes for **dataset** {0}.".format(random_id),

        # "state": "active",  # automatic

        # Let's generate some tags
        "tags": generate_tags(random.randint(0, 10)),

        # Let's put some random stuff in here..
        "extras": generate_extras(random.randint(0, 30)),

        # Some dummy resources
        "resources": resources,

        # Need to be randomized later, to match existing groups
        "groups": [],

        # Need to be randomized later, to match existing orgs
        "owner_org": None,

        # WTF is this thing?
        "relationships": [],
    }


def generate_resource():
    """
    Generate a random resource, to be put in a dataset.

    **Fields:**

    - ``url`` -- resource URL on an "external source"
    - ``resource_type`` -- one of ``api`` or ``file``
    - ``name`` -- random-generated name
    - ``format`` -- a random format (eg: ``csv``, ``json``)
    - ``description`` -- random generated string
    """

    random_id = gen_random_id()
    fmt = random.choice(['csv', 'json'])
    url = 'http://example.com/resource/{0}.{1}'.format(random_id, fmt)
    return {
        "url": url,
        "resource_type": random.choice(['api', 'file']),
        "name": "resource-{0}".format(random_id),
        "format": fmt.upper(),
        "description": "Resource {0}".format(random_id),
    }


def generate_tags(amount):
    """
    Generate ``amount`` random tags.
    Each tag is in the form ``tag-<random-int>``.

    :return: a list of tag names
    """

    return [
        'tag-{0:03d}'.format(random.randint(0, 50))
        for _ in xrange(amount)
    ]


def generate_extras(amount):
    """
    Generate a dict with ``amount`` random key/value pairs.
    """
    pairs = [
        ('key-{0:03d}'.format(random.randint(0, 50)),
         'value {0:03d}'.format(random.randint(0, 50)))
        for _ in xrange(amount)]
    return dict(pairs)


def generate_data(dataset_count=50, orgs_count=10, groups_count=15):
    """
    Generate a bunch of random data.
    Will also associate datasets with random organizations / groups.

    :return: a dict with the ``dataset``, ``organization`` and
        ``group`` keys; each of them a dict of ``{key: object}``.
    """

    data = {'dataset': {}, 'organization': {}, 'group': {}}

    for _ in xrange(orgs_count):
        org = generate_organization()
        data['organization'][org['name']] = org

    for _ in xrange(groups_count):
        group = generate_group()
        data['group'][group['name']] = group

    for _ in xrange(dataset_count):
        dataset = generate_dataset()
        dataset['groups'] = [
            random.choice(data['group'].keys())
            for x in xrange(random.randint(1, 5))
        ]
        dataset['owner_org'] = random.choice(data['organization'].keys())
        data['dataset'][dataset['id']] = dataset

    return data


def generate_id(length=10):
    pool = string.ascii_lowercase + string.digits
    return ''.join(random.choice(pool) for _ in xrange(length))


if __name__ == '__main__':
    import os
    import sys

    if len(sys.argv) > 1:
        destdir = sys.argv[1]
    else:
        destdir = os.getcwd()
    destdir = os.path.abspath(destdir)

    if not os.path.exists(destdir):
        os.makedirs(destdir)
    if not os.path.isdir(destdir):
        raise ValueError("Not a directory: {0}".format(destdir))
    if len(os.listdir(destdir)):
        raise ValueError("Directory not empty: {0}".format(destdir))

    print("Generating data")
    data = generate_data()

    os.chdir(destdir)
    for n in ('dataset', 'group', 'organization'):
        print("Writing {0}".format(n))
        os.makedirs(n)
        for key, val in data[n].iteritems():
            print("    * {0} {1}".format(n, key))
            with open(os.path.join(destdir, n, key), 'w') as f:
                json.dump(val, f)
