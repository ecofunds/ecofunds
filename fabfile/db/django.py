# coding: utf-8
from fabric.api import task, get, env, put, run, cd, require, prefix
from unipath import Path
from ..helpers import timestamp


@task
def dumpdata(apps_or_models=''):
    '''
    Generate a database dump and download it.

    Usage: fab stage db.django.dump
    '''
    require('PROJECT', provided_by=['stage', 'production'])

    remote_file = '%(tmp)s/db-%(instance)s-%(project)s-' % env.PROJECT + timestamp() +'.sql.bz2'

    with cd(env.PROJECT.current):
        with prefix('source bin/activate'):
            run('python manage.py dumpdata %s --indent 4 | bzip2 -c  > %s' % (apps_or_models, remote_file))
            get(remote_file, '.')


@task
def loaddata(local_file):
    '''
    Upload a local database dump and restore it.

    Usage: fab stage db.django.loaddata:dumpfile.bz2
    '''
    require('PROJECT')

    local_file = Path(local_file).absolute()
    remote_file = Path(put(local_file, env.PROJECT.tmp, use_sudo=True)[0])

    if remote_file.endswith('.bz2'):
        sudo('bunzip2 ' + remote_file)
        remote_file = remote_file.parent.child(remote_file.stem)

    with cd(env.PROJECT.current):
        with prefix('source bin/activate'):
            run('python manage.py loaddata %s' % remote_file)

    run('rm %s' % remote_file)

