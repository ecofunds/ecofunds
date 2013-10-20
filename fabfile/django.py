# coding: utf-8
from fabric.api import env, task, settings, hide, cd, run, prefix, get


@task
def manage(command):
    assert command
    with settings(hide('warnings'), warn_only=True):
        with cd(env.PROJECT.current):
            with prefix('source bin/activate'):
                run('python manage.py %s' % command)

@task
def crud_backup():
    with cd(env.PROJECT.current):
        with prefix('source bin/activate'):
            run('python manage.py dumpdata crud.Activity2 crud.Organization2 ' +
                'crud.Project2 crud.Investment2 --indent=4 --format=json ' +
                '> crud.json')
            get('crud.json', 'crud.json')
