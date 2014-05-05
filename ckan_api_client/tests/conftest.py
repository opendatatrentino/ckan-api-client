from __future__ import print_function

from ConfigParser import RawConfigParser
import binascii
import os
import random
import shutil
import socket
import subprocess
import time
import urlparse
import uuid

import psycopg2
import psycopg2.extras
import pytest
import solr

HERE = os.path.abspath(os.path.dirname(__file__))


# Paster command to create users
# ------------------------------
# paster --plugin=ckan user --config=$VIRTUAL_ENV/etc/ckan/production.ini
# add admin password=admin email=admin@example.com api-key=my-api-key

# Paster command to initialize database
# -------------------------------------
# paster --plugin=ckan db --config=$VIRTUAL_ENV/etc/ckan.ini init

# Paster command to rebuild search index
# --------------------------------------
# paster --plugin=ckan search-index --config=$VIRTUAL_ENV/etc/ckan.ini rebuild

# Paster command to run server
# ----------------------------
# paster --plugin=ckan serve $VIRTUAL_ENV/etc/ckan.ini


def check_tcp_port(host, port, timeout=3):
    """Check whether a given TCP port is reachable"""

    s = socket.socket()
    try:
        s.settimeout(timeout)
        s.connect((host, port))
    except socket.error:
        return False
    else:
        s.close()
        return True


def wait_net_service(host, port, timeout):
    """
    Wait for network service to appear

    Based on: http://code.activestate.com/recipes/576655/

    :param timeout: in seconds
    :return: True of False, if timeout is None may return only True or
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
            s.connect((host, port))

        except socket.error:
            pass  # Keep suppressing exceptions

        else:
            # Connection successful!
            s.close()
            return True


def discover_available_port(minport=5000, maxport=9000):
    """Find an available TCP port in the specified range"""
    # We randomize port numbers in order to minimize the risk
    # of collisions when creating two instances at once.
    max_tries = maxport - minport
    for _ in xrange(max_tries):
        portnum = random.randint(minport, maxport)
        if not check_tcp_port(host='127.0.0.1', port=portnum, timeout=3):
            return portnum
    raise RuntimeError("No available port found in the specified range")


class CkanEnvironment(object):
    """
    Class providing functionality to manage a Ckan installation.

    This manages:

    - the virtualenv
    - ckan instance creation
    - database and solr operations
    """

    def __init__(self, venv_root, pgsql_admin_url, solr_url):
        """
        :param venv_root:
            Root path to the virtualenv in which Ckan is installed
        :param pgsql_admin_url:
            URL with administrative credentials to PostgreSQL
        :param solr_url:
            URL to Solr index to be used
        """

        self.venv_root = venv_root
        self.postgresql_admin_url = pgsql_admin_url
        self.solr_url = solr_url

    @classmethod
    def from_environment(cls):
        """
        Alternate constructor: initializes configuration
        by reading environment variables.

        - ``CKAN_VIRTUALENV`` will be used as the virtualenv
          in which Ckan is installed (may differ from current
          virtualenv!).
        - ``CKAN_POSTGRES_ADMIN`` url with administrative
          credentials to be used to access PostgreSQL.
          Example: ``postgresql://postgres:pass@localhost/postgres``
        - ``SOLR_URL`` url of the solr index to use.
        """

        venv_root = os.environ['CKAN_VIRTUALENV']
        pgsql_admin_url = os.environ['CKAN_POSTGRES_ADMIN']
        solr_url = os.environ['CKAN_SOLR']
        return cls(venv_root, pgsql_admin_url, solr_url)

    def create_instance(self):
        instance_id = '{0:06d}'.format(random.randint(0, 999999))

        # Get random port number
        server_host = '127.0.0.1'
        server_port = discover_available_port()

        # Create postgresql user + database
        pg_credentials = self.get_postgres_admin_credentials()
        pg_database = 'ckan_test_{0}'.format(instance_id)
        pg_user = 'ckan_user_{0}'.format(instance_id)
        pg_password = binascii.hexlify(os.urandom(20))

        pg_credentials.update({
            'database': pg_database,
            'user': pg_user,
            'password': pg_password,
        })
        sqlalchemy_url = self.make_postgres_url(**pg_credentials)

        # Actually create database
        self.create_db_user(pg_user, pg_password)
        self.create_db(pg_database, owner=pg_user)

        # Create site id (for Solr)
        site_id = 'ckan_test_{0}'.format(instance_id)
        solr_url = self.solr_url

        # Flush the solr index
        self.flush_solr_index(solr_url=solr_url, site_id=site_id)

        # Storage path
        storage_path = os.path.join(
            self.venv_root, 'var', 'lib', 'ckan-{0}'.format(instance_id))
        os.makedirs(storage_path)

        # Generate configuration file path
        conf_dir = os.path.join(self.venv_root, 'etc', 'ckan')
        if not os.path.exists(conf_dir):
            os.makedirs(conf_dir)
        conf_file_path = os.path.join(
            conf_dir, 'ckan-{0}.ini'.format(instance_id))

        # Prepare configuration
        extra_conf = {
            'server:main': {
                'host': server_host,
                'port': server_port,
            },
            'app:main': {
                'beaker.session.key': self._generate_session_key(),
                'app_instance_uuid': self._generate_instance_uuid(),
                'sqlalchemy.url': sqlalchemy_url,
                'ckan.site_id': site_id,
                'solr_url': solr_url,
                'ckan.storage_path': storage_path,
            }
        }

        # Write configuration file
        conf = self.create_configuration_file(conf_file_path, extra_conf)

        # Instantiate the new CkanInstance
        ckan_instance = CkanInstance(self, conf)

        # Init database using paster command
        ckan_instance.paster_db_init()

        return ckan_instance

    def _generate_session_key(self):
        return binascii.hexlify(os.urandom(20))

    def _generate_instance_uuid(self):
        return '{{{0}}}'.format(str(uuid.uuid4()))

    def get_command(self, name):
        """Return the full path of a command inside the virtualenv"""
        return os.path.join(self.venv_root, 'bin', name)

    def run_paster(self, *args):
        """
        Run a paster command in the virtualenv.

        Arguments will be passed to the paster command invocation.

        Executed command will be something like::

            <venv>/bin/python <venv>/bin/paster --plugin=ckan [<args> ..]
        """

        python = self.get_command('python')
        paster = self.get_command('paster')
        return subprocess.check_call((python, paster, '--plugin=ckan') + args)

    def get_postgres_admin_credentials(self):
        parsed_pg_url = urlparse.urlparse(self.postgresql_admin_url)
        assert parsed_pg_url.scheme == 'postgresql'
        return dict(
            user=parsed_pg_url.username,
            password=parsed_pg_url.password,
            host=parsed_pg_url.hostname,
            port=parsed_pg_url.port or 5432,
            database='postgres')

    def make_postgres_url(self, user, password, host, port, database):
        return urlparse.urlunparse((
            'postgresql',
            '{0}:{1}@{2}:{3}'.format(user, password, host, port),
            database, '', '', ''))

    def get_postgres_admin_connection(self):
        """
        :return: administrative connection to database
        :rtype: psycopg2.connect()
        """
        credentials = self.get_postgres_admin_credentials()
        conn = psycopg2.connect(**credentials)
        conn.set_isolation_level(0)  # So we can DROP stuff
        return conn

    def get_postgres_connection(self, username, password, database):
        """
        :return: "user" connection to database
        :rtype: psycopg2.connect()
        """
        credentials = self.get_postgres_admin_credentials()
        credentials.update({
            'user': username,
            'password': password,
            'database': database,
        })
        conn = psycopg2.connect(**credentials)
        conn.set_isolation_level(0)
        return conn

    def create_db_user(self, username, password):
        """Create PostgreSQL user, for use by Ckan"""

        conn = self.get_postgres_admin_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE ROLE {0} LOGIN
        PASSWORD '{1}'
        NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
        """.format(username, password))

    def create_db(self, name, owner):
        """Create PostgreSQL database, for use by Ckan"""

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
        """.format(name, owner))

    def drop_db_user(self, username):
        """
        Delete previously created PostgreSQL user, to cleanup
        after running tests.
        """

        conn = self.get_postgres_admin_connection()
        cursor = conn.cursor()
        cursor.execute("DROP ROLE {0};".format(username))

    def drop_db(self, name):
        """
        Delete previously created PostgreSQL database, to cleanup
        after running tests.
        """

        conn = self.get_postgres_admin_connection()
        cursor = conn.cursor()
        cursor.execute("DROP DATABASE {0};".format(name))

    def flush_solr_index(self, solr_url=None, site_id=None):
        """
        Completely flush the configured Solr index.

        .. note:: since Ckan supports sharing the same index between
                  installations, we don't actually delete *everything*
                  from the index, but instead issued a delete on query:
                  ``+site_id:"<ckan-site-id>"``
        """

        if solr_url is None:
            solr_url = self.solr_url

        if site_id is None:
            query = '*:*'
        else:
            query = '+site_id:"{0}"'.format(site_id)

        s = solr.SolrConnection(solr_url)
        s.delete_query(query)
        s.commit()
        assert s.query(query).numFound == 0

    def create_configuration_file(self, file_name, extra=None):
        """
        Create a configuration file for Ckan.

        :return: CkanConfFileWrapper associated to conf file
        """

        # Use paster to create the configuration file
        self.run_paster('make-config', 'ckan', file_name)

        # Prepare wrapper object, to allow changes..
        conf = ConfFileWrapper(file_name)

        # Merge extra configuration
        if extra is not None:
            conf.update(extra)

        return conf

    def teardown(self):
        # self.drop_db()
        # self.drop_db_user()
        # self.flush_solr_index()
        # os.unlink(self.conf_file_path)
        # shutil.rmtree(self.storage_path)
        pass

    def __del__(self):
        """Call :py:meth:`teardown` on exit."""
        self.teardown()


class ProcessWrapper(object):
    def __init__(self, args, waitstart=None):
        self.args = args
        self.waitstart = waitstart
        self.process = None

    def start(self):
        self.process = subprocess.Popen(self.args)

        # Wait for the server to come up
        # wait_net_service(self.host, self.port, timeout=20)
        if self.waitstart is not None:
            self.waitstart()

        return self.process

    def stop(self):
        if self.process is None:
            return  # nothing to do here..
        self.process.terminate()
        self.process.wait()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, e_type, exc, tb):
        self.stop()


class ConfFileWrapper(object):
    """
    Wrapper for Ckan configuration files, providing
    some additional functionality.
    """

    def __init__(self, filename):
        self.filename = filename

    def get_conf_parser(self):
        """
        Get a RawConfigParser instance, with configuration loaded
        from the wrapped configuration file.

        Not caching this as we want to reload any changes that should
        have occurred on the file..
        """

        cfp = RawConfigParser()
        cfp.read(self.filename)
        return cfp

    def set(self, section, option, value):
        """Set a configuration option"""
        conf_parser = self.get_conf_parser()
        conf_parser.set(section, option, value)
        conf_parser.write(self.filename)

    def get(self, section, option):
        """Get a configuration option"""
        conf_parser = self.get_conf_parser()
        return conf_parser.get(section, option)

    def delete(self, section, option):
        """Delete a configuration option"""
        conf_parser = self.get_conf_parser()
        conf_parser.remove_option(section, option)
        conf_parser.write(self.filename)

    def update(self, data):
        """
        Update configuration.

        :param dict data:
            dict of dicts: ``{section: {option: value}}``
        """
        conf_parser = self.get_conf_parser()
        for section, sdata in data.iteritems():
            for option, value in sdata.iteritems():
                conf_parser.set(section, option, value)
        with open(self.filename, 'w') as fp:
            conf_parser.write(fp)


class CkanInstance(object):
    """
    Wrapper for a Ckan instance.

    Based on:

    - a virtualenv
    - a Ckan configuration file
    """

    def __init__(self, virtualenv, conf):
        if not isinstance(virtualenv, CkanEnvironment):
            raise TypeError('Expected CkanEnvironment, got {0!r}'
                            .format(type(virtualenv)))

        if not isinstance(conf, ConfFileWrapper):
            raise TypeError('Expected ConfFileWrapper, got {0!r}'
                            .format(type(conf)))

        self.virtualenv = virtualenv
        self.conf = conf

    @property
    def venv_root(self):
        return self.virtualenv.venv_root

    @property
    def server_host(self):
        return self.conf.get('server:main', 'host')

    @property
    def server_port(self):
        return int(self.conf.get('server:main', 'port'))

    @property
    def server_url(self):
        return 'http://{0}:{1}'.format(self.server_host, self.server_port)

    @property
    def configuration_file(self):
        return self.conf.filename

    @property
    def database_url(self):
        return self.conf.get('app:main', 'sqlalchemy.url')

    @property
    def database_name(self):
        db_creds = urlparse.urlparse(self.database_url)
        return db_creds.path.strip('/').split('/')[0]

    @property
    def database_username(self):
        db_creds = urlparse.urlparse(self.database_url)
        return db_creds.username

    @property
    def database_password(self):
        db_creds = urlparse.urlparse(self.database_url)
        return db_creds.password

    @property
    def solr_url(self):
        return self.conf.get('app:main', 'solr_url')

    @property
    def site_id(self):
        return self.conf.get('app:main', 'ckan.site_id')

    @property
    def storage_path(self):
        return self.conf.get('app:main', 'ckan.storage_path')

    def run_paster(self, *a, **kw):
        return self.virtualenv.run_paster(*a, **kw)

    def get_command(self, *a, **kw):
        return self.virtualenv.get_command(*a, **kw)

    def run_paster_with_conf(self, command, *args):
        """
        Run a paster command in the virtualenv, adding --config=ckan.ini

        :param command: the paster command to be run
        :param args: other arguments will be passed to the command

        Executed command will be something like::

            <venv>/bin/python <venv>/bin/paster --plugin=ckan \\
                <command> --config=<venv>/etc/ckan/ckan.ini [<args> ..]
        """

        return self.run_paster(
            command, '--config={0}'.format(self.configuration_file), *args)

    def serve(self):
        """
        Start the Ckan server, using ``paster serve`` command.

        :rtype: :py:class:`CkanServerWrapper`
        """

        python = self.get_command('python')
        paster = self.get_command('paster')

        return ProcessWrapper(
            [python, paster, 'serve', self.configuration_file],
            waitstart=lambda: wait_net_service(
                self.server_host, self.server_port, timeout=30))

    def get_postgres_connection(self):
        db_creds = urlparse.urlparse(self.database_url)
        return self.virtualenv.get_postgres_connection(
            db_creds.username, db_creds.password,
            self.database_name)

    def paster_db_init(self):
        """Initialize database, by calling paster command"""
        return self.run_paster_with_conf('db', 'init')

    def paster_search_index_rebuild(self):
        """Rebuild search index, by calling paster command"""
        return self.run_paster_with_conf('search-index', 'rebuild')

    def paster_user_add(self, name, **kwargs):
        """Create Ckan user, by calling paster command"""

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
        """Remove Ckan user, by calling paster command"""
        return self.run_paster_with_conf('user', 'remove', name)

    def paster_sysadmin_add(self, name):
        """
        Grant sysadmin privileges to a Ckan user,
        by calling paster command.
        """
        return self.run_paster_with_conf('sysadmin', 'add', name)

    def paster_sysadmin_remove(self, name):
        """
        Revoke sysadmin privileges from a Ckan user,
        by calling paster command.
        """
        return self.run_paster_with_conf('sysadmin', 'remove', name)

    def get_sysadmin_api_key(self):
        """
        Create a sysadmin user (with random name / password)
        and return its API key.
        """

        from ckan_api_client.tests.utils.strings \
            import (generate_password, generate_random_alphanum)

        user_name = 'api_test_{0}'.format(generate_random_alphanum(10).lower())
        user_data = self.paster_user_add(user_name, **{
            'password': generate_password(20),
            'email': '{0}@example.com'.format(user_name)})
        self.paster_sysadmin_add(user_name)
        return user_data['apikey']

    def teardown(self):
        # Remove database / user
        db_creds = urlparse.urlparse(self.database_url)
        self.virtualenv.drop_db(db_creds.path.strip('/').split('/')[0])
        self.virtualenv.drop_db_user(db_creds.username)

        # Flush the Solr index
        self.virtualenv.flush_solr_index(self.solr_url, self.site_id)

        # Remove all the storage stuff
        shutil.rmtree(self.storage_path)

        # Delete the configuration file itself
        os.unlink(self.configuration_file)


@pytest.fixture(scope='session')
def ckan_env(request):
    """
    Example usage::

        def test_example(ckan_env):
            instance = ckan_env.create_instance()

            with instance.serve() as server:
                # Now make the client connect to ``server.url``

                # If you need an API key:
                api_key = ckan_env.get_sysadmin_api_key()


    :return: A configured Ckan environment object, ready for use
    :rtype: :py:class:`CkanEnvironment`
    """
    env = CkanEnvironment.from_environment()
    request.addfinalizer(lambda: env.teardown())
    return env


@pytest.fixture(scope='module')
def ckan_instance(request, ckan_env):
    instance = ckan_env.create_instance()
    request.addfinalizer(lambda: instance.teardown())
    return instance


@pytest.fixture(scope='module')
def ckan_url(request, ckan_instance):
    """
    Create & launch a Ckan instance; return a URL at which
    it is accessible.

    Note this would only work for read-only access, as there is no
    way to get an authentication key too..

    :return: URL to access the instance
    :rtype: basestring
    """
    # todo: pass user:apikey in the url? -> but it needs to be stripped..

    server = ckan_instance.serve()

    def finalize():
        server.stop()
    request.addfinalizer(finalize)

    base_url = ckan_instance.server_url

    def get_ckan_url(path):
        return urlparse.urljoin(base_url, path)

    server.start()

    return get_ckan_url


@pytest.fixture
def data_dir():
    """
    Return path to the data directory.

    :rtype: :py:class:`py.path.local`
    """
    import py
    here = py.path.local(__file__).dirpath()
    return here.join('data')


# ------------------------------------------------------------
# Clients

def _get_ckan_client(request, ckan_instance, client_class):
    api_key = ckan_instance.get_sysadmin_api_key()
    server = ckan_instance.serve()
    client = client_class(ckan_instance.server_url, api_key)

    def finalize():
        server.stop()
    request.addfinalizer(finalize)

    server.start()
    return client


@pytest.fixture(scope='module')
def ckan_client_arguments(request, ckan_instance):
    """
    Return arguments to be used to instantiate a new ckan client
    attached to a running ckan instance.
    """

    api_key = ckan_instance.get_sysadmin_api_key()
    server = ckan_instance.serve()
    args = ((ckan_instance.server_url, api_key), {})

    def finalize():
        server.stop()
    request.addfinalizer(finalize)

    server.start()
    return args


@pytest.fixture(scope='module')
def ckan_client_ll(request, ckan_instance):
    """
    :return: A low-level client attached to a running Ckan
    :rtype: :py:class:`ckan_api_client.low_level.CkanLowlevelClient`
    """
    from ckan_api_client.low_level import CkanLowlevelClient
    return _get_ckan_client(request, ckan_instance, CkanLowlevelClient)


@pytest.fixture(scope='module')
def ckan_client_hl(request, ckan_instance):
    """
    :return: A high-level client attached to a running Ckan
    :rtype: :py:class:`ckan_api_client.high_level.CkanHighlevelClient`
    """
    from ckan_api_client.high_level import CkanHighlevelClient
    return _get_ckan_client(request, ckan_instance, CkanHighlevelClient)


@pytest.fixture(scope='module')
def ckan_client_sync(request, ckan_instance):
    """
    :return: A synchronization client attached to a running Ckan
    :rtype: :py:class:`ckan_api_client.syncing.SynchronizationClient`
    """
    from ckan_api_client.syncing import SynchronizationClient
    return _get_ckan_client(request, ckan_instance, SynchronizationClient)


# ------------------------------------------------------------
# More utilities

def diff_eq(left, right):
    from _pytest.assertion.util import assertrepr_compare
    from pytest import config
    for line in assertrepr_compare(config, '==', left, right):
        print(line)
