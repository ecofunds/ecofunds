# coding: utf-8
from fabric.api import task, env
from unipath import Path
from .helpers import Project

# Exposes other functionalities
import setup
import deploy
import db
import config
import django


# Always run fabric from the repository root dir.
Path(__file__).parent.parent.chdir()


@task
def stage():
    env.user = 'ecofunds'
    env.instance = 'stage'
    env.project = 'ecofunds'
    env.package = 'ecofunds'

    env.hosts = ['stage.ecofundsdatabase.org']

    env.settings = '%s.settings' % env.package
    env.PROJECT = Project(user='ecofunds', basedir='/home/ecofunds', instance='stage', project='ecofunds', package='ecofunds')


@task
def production():
    env.user = 'ecofunds'
    env.instance = 'production'
    env.project = 'ecofunds'
    env.package = 'ecofunds'

    env.hosts = ['production.ecofundsdatabase.org']

    env.settings = '%s.settings' % env.package

    env.PROJECT = Project(user='ecofunds', basedir='/home/ecofunds', instance='production', project='ecofunds', package='ecofunds')


"""
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
