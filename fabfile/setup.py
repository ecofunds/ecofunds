# coding: utf-8
from getpass import getpass
from fabric.api import env, run, require, abort, task, warn_only, put, prompt, local, sudo, cd
from fabric.colors import red, yellow
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from unipath import Path
from .helpers import ask


@task
def server(hostname, fqdn, email):
    '''
    Setup a new server: server_setup:hostname,fqdn,email

    Example: server:palmas,palmas.dekode.com.br,admin@dekode.com.br
    '''
    env.user = 'root'

    files = [
        'server/server_setup.sh',
        'server/postfix.sh',
        'server/watchdog.sh',
        'server/uwsgi.sh',
    ]

    # Choose database
    answer = ask('Which database to install? [P]ostgres, [M]ysql, [N]one ',
        options={
            'P': ['server/pg_hba.conf', 'server/postgresql.sh'],
            'M': ['server/mysql.sh'],
            'N': []})

    files.extend(answer)

    # Create superuser
    if 'Y' == ask('Create superuser? [Y]es or [N]o ', options=('Y', 'N')):
        superuser()

    # Upload files and fixes execution mode
    for localfile in files:
        put(localfile, '~/', mirror_local_mode=True)

    run('~root/server_setup.sh %(hostname)s %(fqdn)s %(email)s' % locals())


@task
def application():
    """
    Setup application directories: fab stage setup.application

    We use 1 user for 1 app with N environments.
    This makes easy to give deploy access to different ssh keys.

    The project directory layout is:

      ~/user (rootdir)
      +---- /stage.myproject.com.br (appdir)
      |     +---- /releases
      |     |     +---- /current
      |     +---- /share
      +---- /logs
            +---- /stage.myproject.com.br (logs)
    """
    require('PROJECT', provided_by=['stage', 'production'])

    if exists(env.PROJECT.appdir):
        print(yellow('Application detected at: %(appdir)s' % env.PROJECT))
        if confirm(red('Rebuild application?'), default=False):
            run('rm -rf %(appdir)s' % env.PROJECT)
        else:
            abort('Application already exists.')

    # Create directory structure
    run('mkdir -m 755 -p %(appdir)s' % env.PROJECT)
    run('mkdir -m 755 -p %(releases)s' % env.PROJECT)
    run('mkdir -m 755 -p %(current)s' % env.PROJECT)
    run('mkdir -m 755 -p %(share)s' % env.PROJECT)
    run('mkdir -m 755 -p %(media)s' % env.PROJECT)
    run('mkdir -m 755 -p %(tmp)s' % env.PROJECT)

    with warn_only():
        run('mkdir -m 755 -p %(logs)s' % env.PROJECT)

    # Initialize environment settings file
    run('touch %(settings)s' % env.PROJECT)
    run('chmod 600 %(settings)s' % env.PROJECT)

    # Cria os symlinks configurando os serviços
    with cd('/etc/nginx/sites-enabled/'):
        sudo('ln -sf %s/host/nginx.vhost %s.vhost' % (env.PROJECT.current, env.PROJECT.appname))

    with cd('/etc/supervisor/conf.d'):
        sudo('ln -sf %s/host/app_wsgi.conf %s.conf' % (env.PROJECT.current, env.PROJECT.appname))


@task
def delete_app():
    """
    Delete an application instance.
    """
    require('PROJECT', provided_by=['stage', 'production'])

    question = red('Do you want to DELETE the app at %(appdir)s ?' % env.PROJECT)

    if exists(env.PROJECT.appdir) and confirm(question, default=False):
        run('rm -rf %(appdir)s' % env.PROJECT)


@task
def superuser(pubkey=None, username=None):
    """
    fab env superuser
    """
    env.user = 'root'

    keyfile = Path(pubkey or Path('~', '.ssh', 'id_rsa.pub')).expand()

    if not keyfile.exists():
        abort('Public key file does not exist: %s' % keyfile)

    username = username or prompt('Username: ')
    password = getpass('Password: ')
    password = local('perl -e \'print crypt(\"%s\", \"password\")\'' % (password),
                     capture=True)

    with open(keyfile, 'r') as f:
        pubkey = f.read(65535)

    commands = (
        'useradd -m -s /bin/bash -p {password} {username}',
        'mkdir ~{username}/.ssh -m 700',
        'echo "{pubkey}" >> ~{username}/.ssh/authorized_keys',
        'chmod 644 ~{username}/.ssh/authorized_keys',
        'chown -R {username}:{username} ~{username}/.ssh',
        'usermod -a -G sudo {username}',
    )

    for command in commands:
        run(command.format(**locals()))


@task
def projectuser(pubkey=None, username=None):
    """
    fab env superuser
    """
    keyfile = Path(pubkey or Path('~', '.ssh', 'id_rsa.pub')).expand()

    if not keyfile.exists():
        abort('Public key file does not exist: %s' % keyfile)

    username = username or prompt('Username: ')
    password = getpass('Password: ')
    password = local('perl -e \'print crypt(\"%s\", \"password\")\'' % (password),
                     capture=True)

    with open(keyfile, 'r') as f:
        pubkey = f.read(65535)

    commands = (
        'useradd -m -s /bin/bash -p {password} {username}',
        'mkdir ~{username}/.ssh -m 700',
        'echo "{pubkey}" >> ~{username}/.ssh/authorized_keys',
        'chmod 644 ~{username}/.ssh/authorized_keys',
        'chown -R {username}:{username} ~{username}/.ssh',
        'usermod -a -G sudo {username}',
        'usermod -a -G www-data {username}',
        'echo "{username} ALL=(root) NOPASSWD: /usr/bin/pip, /usr/bin/crontab, /usr/sbin/service, /usr/bin/supervisorctl" >> /etc/sudoers'
    )

    for command in commands:
        sudo(command.format(**locals()))

@task
def remove_user(username):
    '''
        fab env remove_user
    '''
    commands = (
        'userdel {username}',
        'rm -rf /home/{username}',
        "sed -i '/^{username}.*NOPASSWD.*/d' /etc/sudoers"
    )

    for command in commands:
        sudo(command.format(**locals()))
