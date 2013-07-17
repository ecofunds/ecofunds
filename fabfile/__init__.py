# coding: utf-8
from fabric.api import task, env
from unipath import Path
from .helpers import make_environment

# Exposes other functionalities
import setup
import deploy
import db
import config
import django
import mysql5


# Always run fabric from the repository root dir.
Path(__file__).parent.parent.chdir()


@task
def stage():
    from helpers import Project

    env.user = 'ecofunds'
    env.hosts = ['stage.ecofundsdatabase.org']
    env.settings = 'ecofunds.settings'
    env.PROJECT = Project('~', 'stage.ecofunds', 'ecofunds')


@task
def production():
    make_environment('production', 'smallactsmanifesto.org')


"""
# -*- encoding: utf-8 -*-
import getpass
import os
import pwd

from datetime import datetime
from ConfigParser import ConfigParser

from fabric.api import run, env, put, sudo, cd, local, lcd, settings, get, \
                       hide, abort, require, prompt
from fabric.contrib.files import exists
from fabric.colors import red

REMOTE_ROOT = '/opt/'

env.update(
    ENV_ROOT     = REMOTE_ROOT,
    ENV_APPS     = REMOTE_ROOT + '/apps',
    ENV_LOG      = REMOTE_ROOT + '/log',
    ENV_RUN      = REMOTE_ROOT + '/run',
    ENV_BIN      = REMOTE_ROOT + '/bin',
    ENV_CONF     = REMOTE_ROOT + '/conf',
)

# Specify keys
# env.key_filename = [path]
custom_env = {}

def lazy(func):
    def lazyfunc(*args, **kwargs):
        wrapped = lambda : func(*args, **kwargs)
        wrapped.__name__ = "lazy-" + func.__name__
        return wrapped
    return lazyfunc

@lazy
def environment_config(path):
    global custom_env

    config = ConfigParser()
    config.read(path)

    server_address = config.get('environment', 'address')
    app_name = config.get('application', 'name')
    project_user = config.get('environment', 'project_user')
    admin_user = config.get('environment', 'admin_user')

    if project_user == "?":
        project_user = prompt("Project Username: ")

    env.hosts = [server_address]
    env.environment = os.path.basename(path).split('.')[0]
    custom_env['admin_user'] = admin_user
    custom_env['project_user'] = project_user

try:
    files = os.listdir('env')
    for conf_file in files:
        if conf_file.endswith('.cfg'):
            env_name = conf_file.split('.')[0]
            if not env_name in globals():
                globals()[env_name] = environment_config(os.path.join('env', conf_file))
except:
    pass

def config_user(key_path=None):
    '''
        fab env config_user [pub_key_file]
    '''
    env.user = custom_env['admin_user']
    if not key_path:
        key_path = os.path.join(pwd.getpwnam(os.getlogin())[5], ".ssh/id_rsa.pub")

    username = prompt('Username: ')
    password = getpass.getpass("Password: ")
    password = local('perl -e \'print crypt(\"%s\", \"password\")\'' % (password),
                     capture=True)

    ssh_file = open(key_path, "r")
    pub_key = ssh_file.read()

    command_sequence = [
        'useradd -m -s /bin/bash -p {password} {username}',
        'mkdir ~{username}/.ssh -m 700',
        'echo "{pub_key}" >> ~{username}/.ssh/authorized_keys',
        'chmod 644 ~{username}/.ssh/authorized_keys',
        'chown -R {username}:{username} ~{username}/.ssh',
        'usermod -a -G sudo {username}'
    ]

    for command in command_sequence:
        run(command.format(**locals()))

def config_project_user(key_path=None):
    if not key_path:
        key_path = os.path.join(pwd.getpwnam(os.getlogin())[5], ".ssh/id_rsa.pub")

    env.user = custom_env['admin_user']
    username = prompt('Username: ')
    password = getpass.getpass("Password: ")
    password = local('perl -e \'print crypt(\"%s\", \"password\")\'' % (password),
                     capture=True)
    ssh_file = open(key_path, "r")
    pub_key = ssh_file.read()

    command_sequence = [
        'useradd -m -s /bin/bash -p {password} {username}',
        'mkdir ~{username}/.ssh -m 700',
        'echo "{pub_key}" >> ~{username}/.ssh/authorized_keys',
        'chmod 644 ~{username}/.ssh/authorized_keys',
        'chown -R {username}:{username} ~{username}/.ssh',
        'usermod -a -G sudo {username}',
        'usermod -a -G www-data {username}',
        'echo "{username} ALL=(root) NOPASSWD: /usr/bin/pip, /usr/bin/crontab, /usr/sbin/service, /usr/bin/supervisorctl" >> /etc/sudoers'
    ]

    for command in command_sequence:
        run(command.format(**locals()))

def remove_user(username):
    '''
        fab env remove_user
    '''
    env.user = custom_env['admin_user']

    command_sequence = [
        'userdel {username}',
        'rm -rf /home/{username}'
    ]

    for command in command_sequence:
        run(command.format(**locals()))

def remove_project_user(username):
    '''
        fab env remove_user
    '''
    env.user = custom_env['admin_user']

    command_sequence = [
        'userdel {username}',
        'rm -rf /home/{username}',
        "sed -i '/^{username}.*NOPASSWD.*/d' /etc/sudoers"
    ]

    for command in command_sequence:
        run(command.format(**locals()))

def server_bootstrap(hostname, fqdn, email):
    '''
        Setup a new server: server_setup:hostname,fqdn,email
        Example: server_bootstrap:loogica,loogica.net,felipecruz@loogica.net
    '''
    env.user='root'

    install_db = prompt('Install Database? (Y)es or (N)o')
    if install_db not in ('y', 'n', 'Y', 'N'):
        raise Exception("Valid Answers Y or N")

    pg_mysql = None
    if install_db in ('Y', 'y'):
        pg_mysql = prompt('(P)ostgreSQL or (M)ySQL ?')
        if pg_mysql not in ('p', 'P', 'm', 'M'):
            raise Exception("Valid Answers P or M")


    try:
        secret_file = open('secret_key', 'r')
    except:
        raise Exception("You must have a secret_key file in this path")


    scripts = {
        'server/server_setup.sh':   '/root/server_setup.sh',
        'server/postfix.sh':        '/root/postfix.sh',
        'server/uwsgi.sh':          '/root/uwsgi.sh',
        'server/server_db_setup.sh':'/root/server_db_setup.sh',
        'server/install_mysql.sh':  '/root/install_mysql.sh',
    }

    # Upload files and fixes execution mode
    for localfile, remotefile in scripts.items():
        put(localfile, remotefile, use_sudo=True)
        if remotefile.endswith('.sh'):
            sudo('chmod +x ' + remotefile)

    sudo('/root/server_setup.sh %(hostname)s %(fqdn)s %(email)s' % locals())

    sudo("mkdir -m 755 -p %(ENV_ROOT)s" % env)
    sudo("mkdir -m 755 -p %(ENV_APPS)s" % env)
    sudo("mkdir -m 755 -p %(ENV_LOG)s" % env)
    sudo("mkdir -m 755 -p %(ENV_RUN)s" % env)
    sudo("mkdir -m 755 -p %(ENV_BIN)s" % env)
    sudo("mkdir -m 755 -p %(ENV_CONF)s" % env)
    sudo("mkdir -m 755 -p %(ENV_LOG)s/nginx" % env)
    put('secret_key', '%(ENV_CONF)s/secret_key' % env, use_sudo=True)
    sudo("touch %(ENV_RUN)s/nginx.pid" % env)
    sudo("chown -R ecofunds:www-data %(ENV_ROOT)s" % env)

    if install_db in ('Y', 'y'):
        if pg_mysql in ('P', 'p'):
            sudo('/root/server_db_setup.sh')
        else:
            sudo('/root/install_mysql.sh')


def server_db_install():
    '''
        Install PostgreSQL
    '''
    env.user=ADMIN_USER

    scripts = {
        'server/server_db_setup.sh':   '/root/server_db_setup.sh',
    }

    # Upload files and fixes execution mode
    for localfile, remotefile in scripts.items():
        put(localfile, remotefile, use_sudo=True)
        if remotefile.endswith('.sh'):
            sudo('chmod +x ' + remotefile)

    sudo('/root/server_db_setup.sh')


def setup_app():
    '''
        Initial app setup
    '''
    env.user=ADMIN_USER

    with cd("%s" % (env.ENV_APPS)):
        sudo('mkdir %s' % (APP_NAME))

    with cd("%s" % (env.ENV_LOG)):
        sudo('mkdir %s' % (APP_NAME))

    sudo("chown -R deploy:www-data %(ENV_ROOT)s" % env)


def create_meta_info():
    local(': > %s.meta' % (APP_NAME))
    local('git rev-parse HEAD > %s.meta' % (APP_NAME))
    local('git log  --oneline -20 --format="%h %s %an" >> {0}.meta'.format(APP_NAME))
    return "%s.meta" % (APP_NAME)


def _create_git_archive(revision):
    rev = local('git rev-parse %s' % revision, capture=True)
    archive = '/tmp/%s.tar.bz2' % rev

    local('./git-archive-all.sh -c %s | bzip2 -c > %s' % (rev, archive))

    return archive


def _upload_source(revision, project_dir):
    archive = _create_git_archive(revision)
    meta_file = create_meta_info()

    timestamp = run('date +%Y-%m-%d-%Hh%Mm%Ss')
    release_dir = os.path.join(project_dir, timestamp)

    put(archive, archive)
    put(meta_file, os.path.join(env.ENV_APPS, '%s.meta' % (APP_NAME)))

    run('mkdir -p %s' % release_dir)
    run('tar jxf %s -C %s' % (archive, release_dir))

    run('rm -v %s' % (archive))
    local('rm -f %s' % (meta_file))

    return release_dir


def deploy(revision, first=False):
    '''
    Make the application deploy.

    Example: fab production deploy:1.2
    '''
    env.user = DEPLOY_USER
    project_dir = os.path.join(env.ENV_APPS, APP_NAME)
    current_dir = os.path.join(project_dir, "current")
    current_static = os.path.join(current_dir, APP_NAME)
    current_static = os.path.join(current_static, "static")
    release_dir = _upload_source(revision, project_dir)

    with cd(project_dir):
        run('rm -rf current')
        run('ln -s %s current' % release_dir)

    with cd('/etc/nginx/sites-enabled/'):
        sudo('ln -sf %s/env/app.vhost %s.vhost' % (release_dir, APP_NAME))

    with cd('/etc/supervisor/conf.d'):
        sudo('ln -sf %s/env/app_wsgi.conf %s.conf' % (release_dir, APP_NAME))

    with cd(current_static): #TODO It would be nice configure this
        sudo('sudo ln -s /usr/local/lib/python2.7/dist-packages/django/contrib/admin/static/admin/ admin')

    with cd(release_dir):
        run("make update_deps")
        if first:
            run("make server_dbinitial")
        run("make migrate_no_input")

    run('sudo service nginx restart')
    run('sudo supervisorctl reload')


def first_deploy(revision):
    deploy(revision, first=True)


def postgres_db_create(dbuser, dbname, password):
    '''
        Create a Psql Database: db_create:dbuser,dbname,password

    Example: db_create:username,databasename,password
    '''
    env.user=ADMIN_USER

    prod_settings_file = local('find . | grep settings/production.py', capture=True)
    temp_prod_settings_file = prod_settings_file.replace('/p', '/_p')
    local('sed "s/\$PROD_USER/%s/g;s/\$PROD_PASS/%s/g" %s > %s' % (dbuser,
                                                                   password,
                                                                   prod_settings_file,
                                                                   temp_prod_settings_file))
    local('mv %s %s' % (temp_prod_settings_file, prod_settings_file))
    local('git add %s' % (prod_settings_file))
    local('git commit -m "envkit: set database config"')

    sudo('psql template1 -c "CREATE USER %s WITH CREATEDB ENCRYPTED PASSWORD \'%s\'"' % (dbuser, password), user='postgres')
    sudo('createdb "%s" -O "%s"' % (dbname, dbuser), user='postgres')
    sudo('psql %s -c "CREATE EXTENSION unaccent;"' % dbname, user='postgres')
    sudo('rm -f /etc/postgresql/9.1/main/postgresql.conf')
    put('env/postgresql.conf', '/etc/postgresql/9.1/main/postgresql.conf', use_sudo=True)

    sudo('service postgresql restart')


def add_ip_to_database(ip):
    sudo('echo "host    all    all    %s/32   md5" >> /etc/postgresql/9.1/main/pg_hba.conf' % ip)
    sudo('service postgresql restart')


def nginx_setup():
    '''
        Configure nginx conf file
    '''
    env.user=DEPLOY_USER

    confs = {
        'env/nginx.conf': '/opt/conf/nginx.conf',
    }

    for localfile, remotefile in confs.items():
        put(localfile, remotefile)

    with cd('/etc/nginx/'):
        sudo('ln -sf %s/nginx.conf nginx.conf' % env.ENV_CONF)
        sudo("chown -R deploy:www-data %(ENV_ROOT)s" % env)

    sudo('service nginx restart')


def log(basename=''):
    '''
    fab log                      >> List available logs.
    fab log:nginx/access         >> Tail nginx_access.log
    fab log:nginx_access         >> Tail nginx_access.log
    fab log:uwsgi                 >> Tail uwsgi.log
    '''
    # List available logs
    if not basename:
        with hide('running'):
            with cd(env.PROJECT_LOG):
                run('ls -1')
                exit()

    # Normaliza o basename
    if not basename.endswith('.log'):
        basename += '.log'

    logfile = env.PROJECT_LOG + '/' + basename

    if not exists(logfile):
        abort('Logfile: %s not found.' % logfile)

    run('tail -f ' + logfile)
"""
