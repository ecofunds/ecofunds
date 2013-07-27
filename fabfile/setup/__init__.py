# coding: utf-8
from getpass import getpass
from fabric.api import env, run, require, abort, task, put, prompt, local, sudo, cd, puts, hide, settings
from fabric.colors import red, yellow
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from fabric.tasks import Task
from unipath import Path
from ..helpers import ask


@task
def server(hostname, fqdn, email):
    '''
    Setup a new server: server_setup:hostname,fqdn,email

    Example: server:palmas,palmas.dekode.com.br,admin@dekode.com.br
    '''
    env.user = 'root'

    scripts = Path(__file__).parent.child('scripts')

    files = [
        scripts.child('server_setup.sh'),
        scripts.child('postfix.sh'),
        scripts.child('watchdog.sh'),
        scripts.child('uwsgi.sh'),
    ]

    # Choose database
    answer = ask('Which database to install? [P]ostgres, [M]ysql, [N]one ',
        options={
            'P': [scripts.child('pg_hba.conf'), scripts.child('postgresql.sh')],
            'M': [scripts.child('mysql.sh')],
            'N': []})

    files.extend(answer)

    # Create superuser
    if 'Y' == ask('Create superuser? [Y]es or [N]o ', options=('Y', 'N')):
        createuser.run(as_root=True)

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
    require('PROJECT')

    app_user = env.user

    with settings(user=env.local_user):
        with hide('running', 'stdout', 'stderr'):
            app_user_exists = run('getent passwd %s' % app_user, warn_only=True)

        if not app_user_exists:
            puts("Creating project user: %s" % app_user)
            createprojectuser.run(username=app_user)

    if exists(env.PROJECT.appdir):
        print(yellow('Application detected at: %(appdir)s' % env.PROJECT))
        if confirm(red('Rebuild application?'), default=False):
            run('rm -rf %(appdir)s' % env.PROJECT)
        else:
            abort('Application already exists.')

    # Create directory structure
    for directory in env.PROJECT.dirs.values():
        run('mkdir -m 755 -p %s' % directory)

    # Initialize environment settings file
    run('touch %(settings)s' % env.PROJECT)
    run('chmod 600 %(settings)s' % env.PROJECT)
    run('echo "[settings]" > %(settings)s' % env.PROJECT)

    # Cria os symlinks configurando os serviços
    with cd('/etc/nginx/conf.d/'):
        sudo('ln -sf %(current)s/host/nginx.conf %(appname)s.conf' % env.PROJECT)

    with cd('/etc/nginx/sites-enabled/'):
        sudo('ln -sf %s/host/nginx.vhost %s.vhost' % (env.PROJECT.current, env.PROJECT.appname))

    with cd('/etc/supervisor/conf.d'):
        sudo('ln -sf %s/host/app_wsgi.conf %s.conf' % (env.PROJECT.current, env.PROJECT.appname))


@task
def delete_app():
    """
    Delete an application instance.
    """
    require('PROJECT')

    question = red('Do you want to DELETE the app at %(appdir)s ?' % env.PROJECT)

    if exists(env.PROJECT.appdir) and confirm(question, default=False):
        run('rm -rf %(appdir)s' % env.PROJECT)


class CreateUser(Task):
    name = "createuser"

    def __init__(self):
        super(CreateUser, self).__init__()
        self.commands = (
            'useradd -m -s /bin/bash -p {password} {username}',
            'mkdir ~{username}/.ssh -m 700',
            'echo "{pubkey}" >> ~{username}/.ssh/authorized_keys',
            'chmod 644 ~{username}/.ssh/authorized_keys',
            'chown -R {username}:{username} ~{username}/.ssh',
            'usermod -a -G sudo {username}',
        )

    def run(self, username=None, pubkey=None, as_root=False):
        if as_root:
            env.user = 'root'
            execute = run
        else:
            env.user = env.local_user
            execute = sudo

        keyfile = Path(pubkey or Path('~', '.ssh', 'id_rsa.pub')).expand()

        if not keyfile.exists():
            abort('Public key file does not exist: %s' % keyfile)

        with open(keyfile, 'r') as f:
            pubkey = f.read(65535)

        username = username or prompt('Username: ')
        password = getpass("%s's password: " % username)

        with hide('running', 'stdout', 'stderr'):
            password = local('perl -e \'print crypt(\"%s\", \"password\")\'' % (password),
                         capture=True)

        for command in self.commands:
            execute(command.format(**locals()))

createuser = CreateUser()


class CreateProjectUser(CreateUser):
    name = 'createprojectuser'
    def __init__(self):
        super(CreateProjectUser, self).__init__()
        self.commands = self.commands + (
            'usermod -a -G www-data {username}',
            'echo "{username} ALL=(root) NOPASSWD: /usr/bin/pip, /usr/bin/crontab, /usr/sbin/service, /usr/bin/supervisorctl" >> /etc/sudoers',
            'echo "export PIP_DOWNLOAD_CACHE=~/.pip" >> ~{username}/.profile',
            'echo "export PIP_DOWNLOAD_CACHE=~/.pip" >> ~{username}/.bashrc',
        )

createprojectuser = CreateProjectUser()


@task
def remove_user(username):
    '''
        fab env remove_user
    '''
    env.user = env.local_user

    commands = (
        'userdel {username}',
        'rm -rf /home/{username}',
        "sed -i '/^{username}.*NOPASSWD.*/d' /etc/sudoers"
    )

    for command in commands:
        sudo(command.format(**locals()))
