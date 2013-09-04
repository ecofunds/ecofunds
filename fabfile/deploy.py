# coding: utf-8
from unipath import Path
from fabric.api import task, local, run, cd, put, env, prefix, require, puts, sudo
from fabric.colors import yellow
from fabric.contrib.files import upload_template
from fabric.contrib.project import rsync_project
from .helpers import timestamp


@task
def push(revision):
    """
    Push the code to the right place on the server.
    """
    rev = local('git rev-parse %s' % revision, capture=True)
    local_archive = Path('%s.tar.bz2' % rev)
    remote_archive = Path(env.PROJECT.tmp, local_archive.name)

    local('git archive --format=tar %s | bzip2 -9 -c > %s' % (rev, local_archive))
    put(local_archive, env.PROJECT.tmp)

    release_dir = Path(env.PROJECT.releases, timestamp())
    run('mkdir -p %s' % release_dir)
    run('tar jxf %s -C %s' % (remote_archive, release_dir))

    # cleanup
    local('rm %s' % local_archive)

    puts(yellow('Release Directory: ' + release_dir))
    return release_dir


@task
def build(release_dir):
    """
    Build the pushed version installing packages, running migrations, etc.
    """
    host_files = Path('host').listdir()
    for host_file in host_files:
        upload_template(host_file, '%s/host/' % release_dir, env.PROJECT, backup=False)

    with cd(release_dir):
        release_media = Path(release_dir, env.PROJECT.package, 'media')
        release_settings = Path(release_dir, env.PROJECT.package, 'settings.ini')

        run('ln -sf %s %s' % (env.PROJECT.settings, release_settings))
        run('ln -sf %s %s' % (env.PROJECT.media, release_media))

        run("virtualenv .")
        with prefix('source bin/activate'):
            run("pip install -r requirements.txt")
            run("python manage.py syncdb --noinput")
            run("python manage.py collectstatic --noinput")


@task
def release(release_dir):
    """
    Release the current build activating it on the server.
    """
    with cd(env.PROJECT.releases):
        run('rm -rf current')
        run('ln -s %s current' % release_dir)


@task
def restart():
    """
    Restart all services.
    """
    sudo('service nginx restart', pty=False, shell=False)
    sudo('supervisorctl reload', pty=False, shell=False)


@task(default=True)
def deploy(revision):
    """
    Make the application deploy.

    Example: fab production deploy:1.2
    """
    require('PROJECT', provided_by=['stage', 'production'])

    release_dir = push(revision)
    build(release_dir)
    release(release_dir)
    restart()


@task
def rsync_media(upload=False, delete=False):
    require('PROJECT')

    local_dir = add_slash(Path(env.PROJECT.package, 'media'))
    remote_dir = add_slash(env.PROJECT.media)

    rsync_project(remote_dir, local_dir, delete=delete, upload=upload)


def add_slash(path):
    if not path.endswith('/'):
        path = path + '/'
    return path
