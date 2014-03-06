#!/usr/bin/env python

"""
Recreate PostgreSQL database
"""

# We need:
# - Ckan configuration file (for db connection url)
# - PostgreSQL administrative credentials

from __future__ import print_function

from ConfigParser import RawConfigParser
import os
import sys
import subprocess
import urlparse

import psycopg2
import psycopg2.extras
import solr


def color_print(col, *a, **kw):
    sep = kw.get('sep', ' ')
    a = ['\033[{0}m'.format(col),
         sep.join(a),
         '\033[0m']
    kw['sep'] = ''
    return print(*a, **kw)


def get_postgres_connection(host, port, user, password, database):
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database)
    conn.set_isolation_level(0)
    return conn


def recreate_db(admin_connection, user, database):
    ## Try dropping database
    ##----------------------------------------
    color_print('1;36', "Dropping database (if exists) {0}".format(database))
    cur = admin_connection.cursor()
    cur.execute("""DROP DATABASE IF EXISTS "{0}";""".format(database))

    ## Recreate database
    ##----------------------------------------
    color_print('1;36',
                "Creating database {0} (owned by {1})".format(database, user))
    cursor = admin_connection.cursor()
    cursor.execute("""
    CREATE DATABASE "{db}"
    WITH OWNER = "{user}"
    ENCODING = 'UTF8'
    TABLESPACE = pg_default
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    CONNECTION LIMIT = -1;
    """.format(db=database, user=user))


def rebuild_db_schema(conf_file):
    ## Run paster to recreate schema
    ##----------------------------------------

    color_print('1;36', "Running paster db init")
    command = ['paster', '--plugin=ckan', 'db',
               '--conf={0}'.format(conf_file), 'init']
    subprocess.call(command)


def flush_solr(solr_url, site_id):
    """Empty this solr index"""
    s = solr.SolrConnection(solr_url)
    query = '+site_id:"{0}"'.format(site_id)
    s.delete_query(query)
    s.commit()
    assert s.query(query).numFound == 0


def reindex_solr(conf_file):
    color_print('1;36', "Running paster search-index rebuild")
    command = ['paster', '--plugin=ckan', 'search-index',
               '--conf={0}'.format(conf_file), 'rebuild']
    subprocess.call(command)


def create_superuser(conf_file, conn):
    username = 'admin'

    color_print('1;36', "Creating admin user: {0}".format(username))
    command = ['paster', '--plugin=ckan', 'user',
               '--conf={0}'.format(conf_file), 'add',
               username, 'email={0}@e.com'.format(username),
               'password=password']
    subprocess.call(command)

    color_print('1;36', "Setting as sysadmin")
    command = ['paster', '--plugin=ckan', 'sysadmin',
               '--conf={0}'.format(conf_file), 'add', username]
    subprocess.call(command)

    ## Fetch the newly created user object
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT "name", "apikey" FROM "user" WHERE name=\'{0}\''
                .format(username))
    return cur.fetchone()


def url_to_pg_credentials(url):
    parsed = urlparse.urlparse(url)
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'user': parsed.username,
        'password': parsed.password,
        'database': filter(None, parsed.path.split('/'))[0],
    }


if __name__ == '__main__':
    try:
        CONF_FILE = os.environ.get('CKAN_CONF')
        if not CONF_FILE:
            VIRTUAL_ENV = os.environ['VIRTUAL_ENV']
            CONF_FILE = os.path.join(
                VIRTUAL_ENV, 'etc', 'ckan', 'production.ini')
            if not os.path.exists(CONF_FILE):
                ## Ok, the file is definitely not there..
                raise KeyError

    except KeyError:
        # todo: we could guess $VIRTUAL_ENV/etc/ckan/production.ini
        print("You must pass CKAN_CONF environment variable")
        print("CKAN_CONF=/path/to/configuration/file")
        sys.exit(1)

    try:
        PG_ADMIN = os.environ['PG_ADMIN']
    except KeyError:
        print("You must pass PG_ADMIN environment variable")
        print("PG_ADMIN=username:password")
        sys.exit(1)

    conf = RawConfigParser()
    conf.read(CONF_FILE)

    postgresql_url = conf.get('app:main', 'sqlalchemy.url')
    credentials = url_to_pg_credentials(postgresql_url)
    admin_credentials = credentials.copy()
    admin_user, admin_password = PG_ADMIN.split(':', 1)
    admin_credentials.update({
        'user': admin_user,
        'password': admin_password,
        'database': 'postgres',  # administrative db
    })

    admin_connection = get_postgres_connection(**admin_credentials)

    solr_url = conf.get('app:main', 'solr_url')
    site_id = conf.get('app:main', 'ckan.site_id')

    ## First, make sure db / index are empty
    recreate_db(admin_connection, credentials['user'], credentials['database'])
    flush_solr(solr_url, site_id)

    ## Then, rebuild schemas
    rebuild_db_schema(CONF_FILE)
    reindex_solr(CONF_FILE)

    ## And create superuser
    user_connection = get_postgres_connection(**credentials)
    user = create_superuser(CONF_FILE, user_connection)
    apikey = user['apikey']

    ## Store API key
    color_print("1;32", "Newly created user (admin:password) "
                "has api key: {0}".format(apikey))
    with open('.apikey', 'w') as f:
        f.write(apikey)
