from ConfigParser import RawConfigParser
import binascii
import os
import random
import shutil
import subprocess
import time
import urlparse

import psycopg2
import psycopg2.extras
import pytest
import solr

HERE = os.path.abspath(os.path.dirname(__file__))


## Paster command to create users:
# paster --plugin=ckan user --config=$VIRTUAL_ENV/etc/ckan/production.ini
# add admin password=admin email=admin@example.com api-key=my-api-key

## Paster command to initialize database
# paster --plugin=ckan db --config=$VIRTUAL_ENV/etc/ckan.ini init

## Paster command to rebuild search index
# paster --plugin=ckan search-index --config=$VIRTUAL_ENV/etc/ckan.ini rebuild

## Paster command to run server
# paster --plugin=ckan serve $VIRTUAL_ENV/etc/ckan.ini


def wait_net_service(server, port, timeout):
    """
    Wait for network service to appear

    Based on: http://code.activestate.com/recipes/576655/

    @param timeout: in seconds
    @return: True of False, if timeout is None may return only True or
             throw unhandled network exception
    """
    import socket

    s = socket.socket()
    end = time.time() + timeout

    while True:

        try:
            next_timeout = end - time.time()
            if next_timeout < 0:
                raise Exception("Timed out")

            s.settimeout(next_timeout)
            s.connect((server, port))

        except socket.error:
            pass  # Keep suppressing exceptions

        else:
            # Connection successful!
            s.close()
            return True


class CkanEnvironment(object):
    def __init__(self, venv_root, pgsql_admin_url, solr_url):
        self.venv_root = venv_root

        ## This will be generated temporarily
        self.postgresql_admin_url = pgsql_admin_url
        self.solr_url = solr_url

        self.setup()

    @classmethod
    def from_environment(cls):
        """Initialize by loading stuff from the environment"""

        venv_root = os.environ['CKAN_VIRTUALENV']
        pgsql_admin_url = os.environ['CKAN_POSTGRES_ADMIN']
        solr_url = os.environ['CKAN_SOLR']
        return cls(venv_root, pgsql_admin_url, solr_url)

    @classmethod
    def get_ephemeral_port(cls):
        """Ugly hack to allocate an ephemeral port"""

        import socket
        sock = socket.socket(socket.AF_INET)
        sock.bind(('127.0.0.1', 0))
        addr, port = sock.getsockname()
        sock.close()
        return port

    def get_conf_parser(self):
        """
        Get a RawConfigParser instance, associated with the main
        Ckan configuration file.

        Not caching this as we want to reload any changes that should
        have occurred on the file..
        """

        cfp = RawConfigParser()
        cfp.read(self.conf_file_path)
        return cfp

    def conf_set(self, section, option, value):
        conf_parser = self.get_conf_parser()
        conf_parser.set(section, option, value)
        conf_parser.write(self.conf_file_path)

    def conf_get(self, section, option):
        conf_parser = self.get_conf_parser()
        return conf_parser.get(section, option)

    def conf_del(self, section, option):
        conf_parser = self.get_conf_parser()
        conf_parser.remove_option(section, option)
        conf_parser.write(self.conf_file_path)

    def conf_update(self, data):
        conf_parser = self.get_conf_parser()
        for section, sdata in data.iteritems():
            for option, value in sdata.iteritems():
                conf_parser.set(section, option, value)
        with open(self.conf_file_path, 'w') as fp:
            conf_parser.write(fp)

    def get_postgres_admin_connection(self):
        conn = psycopg2.connect(
            host=self.postgresql_host,
            port=self.postgresql_port,
            user=self.postgresql_admin_user,
            password=self.postgresql_admin_password,
            database='postgres')
        conn.set_isolation_level(0)
        return conn

    def get_postgres_connection(self):
        conn = psycopg2.connect(
            host=self.postgresql_host,
            port=self.postgresql_port,
            user=self.postgresql_user,
            password=self.postgresql_password,
            database=self.postgresql_db_name)
        conn.set_isolation_level(0)
        return conn

    def create_db_user(self):
        conn = self.get_postgres_admin_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE ROLE {0} LOGIN
        PASSWORD '{1}'
        NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
        """.format(self.postgresql_user, self.postgresql_password))

    def create_db(self):
        conn = self.get_postgres_admin_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE DATABASE {0}
          WITH OWNER = {1}
               ENCODING = 'UTF8'
               TABLESPACE = pg_default
               LC_COLLATE = 'en_US.UTF-8'
               LC_CTYPE = 'en_US.UTF-8'
               CONNECTION LIMIT = -1;
        """.format(self.postgresql_db_name,
                   self.postgresql_user))

    def drop_db_user(self):
        conn = self.get_postgres_admin_connection()
        cursor = conn.cursor()
        cursor.execute("DROP ROLE {0};".format(self.postgresql_user))

    def drop_db(self):
        conn = self.get_postgres_admin_connection()
        cursor = conn.cursor()
        cursor.execute("DROP DATABASE {0};".format(self.postgresql_db_name))

    def flush_solr_index(self):
        """Completely flush the configured Solr index"""

        s = solr.SolrConnection(self.solr_url)
        #query = '*:*'
        query = '+site_id:"{0}"'.format(self.site_id)
        s.delete_query(query)
        s.commit()
        assert s.query(query).numFound == 0

    def run_paster(self, *args):
        """Run a paster command in the virtualenv"""

        python = os.path.join(self.venv_root, 'bin', 'python')
        paster = os.path.join(self.venv_root, 'bin', 'paster')
        return subprocess.check_call((python, paster, '--plugin=ckan') + args)

    def run_paster_with_conf(self, command, *args):
        """Run a paster command in the virtualenv, adding --config=ckan.ini"""

        return self.run_paster(
            command, '--config={0}'.format(self.conf_file_path), *args)

    def serve(self):
        """Run the paster server"""

        python = os.path.join(self.venv_root, 'bin', 'python')
        paster = os.path.join(self.venv_root, 'bin', 'paster')

        return CkanServerWrapper([
            python, paster, 'serve', self.conf_file_path
        ], host='127.0.0.1', port=self.server_port)

    def paster_db_init(self):
        return self.run_paster_with_conf('db', 'init')

    def paster_search_index_rebuild(self):
        return self.run_paster_with_conf('search-index', 'rebuild')

    def paster_user_add(self, name, **kwargs):
        args = ['{0}={1}'.format(k, v) for (k, v) in kwargs.iteritems()]
        self.run_paster_with_conf('user', 'add', name, *args)
        # todo: retrieve user from database
        # select name, apikey from "user" where name='';
        conn = self.get_postgres_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT "name", "apikey" FROM "user" WHERE name=\'{0}\''
                    .format(name))
        return cur.fetchone()

    def paster_user_remove(self, name):
        return self.run_paster_with_conf('user', 'remove', name)

    def paster_sysadmin_add(self, name):
        return self.run_paster_with_conf('sysadmin', 'add', name)

    def paster_sysadmin_remove(self, name):
        return self.run_paster_with_conf('sysadmin', 'remove', name)

    def setup(self):
        ## Prepare IDs & names
        my_id = '{0:06d}'.format(random.randint(0, 1e6))

        ## Configuration file
        self.conf_file_path = os.path.join(
            self.venv_root, 'etc', 'ckan-{0}.ini'.format(my_id))

        ## Storage path
        self.storage_path = os.path.join(
            self.venv_root, 'var', 'lib', 'ckan-{0}'.format(my_id))
        os.makedirs(self.storage_path)

        ## Port on which server will listen
        #self.server_port = self.get_ephemeral_port()
        self.server_port = 5000

        parsed_pg_url = urlparse.urlparse(self.postgresql_admin_url)
        assert parsed_pg_url.scheme == 'postgresql'
        credentials, host = parsed_pg_url.netloc.split('@')
        (self.postgresql_admin_user,
         self.postgresql_admin_password) = credentials.split(':')

        if ':' in host:
            host, port = host.split(':')
        else:
            port = 5432
        self.postgresql_host = host
        self.postgresql_port = port

        self.postgresql_db_name = 'ckan_test_{0}'.format(my_id)
        self.postgresql_user = 'ckan_user_{0}'.format(my_id)
        self.postgresql_password = binascii.hexlify(os.urandom(20))

        self.site_id = 'ckan_test_{0}'.format(my_id)

        ## Make sure the configuration directory is there
        conf_dir = os.path.dirname(self.conf_file_path)
        if not os.path.exists(conf_dir):
            os.makedirs(conf_dir)

        ## Create a configuration file
        self.run_paster('make-config', 'ckan', self.conf_file_path)
        self.conf_update({
            'server:main': {
                'host': '0.0.0.0',
                'port': self.server_port,
            },
            'app:main': {
                'beaker.session.key': 'beaker-session-key-here',
                'app_instance_uuid': '{00001111-2222-3333-4444-555566667777}',
                'sqlalchemy.url': urlparse.urlunparse((
                    'postgresql',
                    '{0}:{1}@{2}:{3}'.format(
                        self.postgresql_user, self.postgresql_password,
                        self.postgresql_host, self.postgresql_port),
                    self.postgresql_db_name,
                    '', '', ''
                )),
                'ckan.site_id': self.site_id,
                'solr_url': self.solr_url,
                #'ofs.impl': 'pairtree',
                #'ofs.storage_dir': '',
                'ckan.storage_path': self.storage_path,
            }
        })

        ## Create database
        self.create_db_user()
        self.create_db()

        ## Make sure the Solr index is clear
        self.flush_solr_index()

        ## Initialize database
        self.paster_db_init()

    def teardown(self):
        self.drop_db()
        self.drop_db_user()
        self.flush_solr_index()
        os.unlink(self.conf_file_path)
        shutil.rmtree(self.storage_path)

    def __del__(self):
        self.teardown()


class CkanServerWrapper(object):
    def __init__(self, args, host, port):
        self.args = args
        self.host = host
        self.port = port

    @property
    def url(self):
        return 'http://{host}:{port}/'.format(host=self.host, port=self.port)

    def start(self):
        self.process = subprocess.Popen(self.args)

        ## Wait for the server to come up
        wait_net_service(self.host, self.port, timeout=20)
        return self.process

    def stop(self):
        self.process.terminate()
        self.process.wait()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, e_type, exc, tb):
        self.stop()


@pytest.fixture(scope='session')
def ckan_env():
    return CkanEnvironment.from_environment()


@pytest.fixture(scope='module')
def ckan_url(request, ckan_env):
    server = ckan_env.serve()

    def finalize():
        server.stop()
    request.addfinalizer(finalize)

    base_url = server.url

    def get_ckan_url(path):
        return urlparse.urljoin(base_url, path)

    server.start()

    return get_ckan_url


@pytest.fixture
def api_key():
    return os.environ.get('API_KEY', 'my-api-key')
