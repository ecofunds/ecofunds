# coding: utf-8
from datetime import datetime
from fabric.api import settings, require
from fabric.tasks import Task
from cuisine import MODE_SUDO

class Project(dict):
    """
    Describes the remote directory structure for a project.
    """
    def __init__(self, user, basedir, instance, project, package):
        appname = '%s.%s' % (instance, project)
        appdir = '%s/%s' % (basedir, appname)

        self.dirs = dict(
            appdir   = appdir,
            releases = '%s/releases' % appdir,
            current  = '%s/releases/current' % appdir,
            share    = '%s/share' % appdir,
            media    = '%s/share/media' % appdir,
            tmp      = '%s/tmp' % appdir,
            logs     = '%s/logs' % appdir,
        )

        super(Project, self).__init__(
            user=user,
            instance=instance,
            project=project,
            appname=appname,
            package=package,
            settings='%s/share/settings.ini' % appdir,
            **self.dirs)

    def __getattr__(self, item):
        if item in self:
            return self[item]

        raise AttributeError("'%s' object has no attribute '%s'" % (
            self.__name__, item))


def timestamp():
    return datetime.now().strftime("%Y-%m-%d-%Hh%Mm%Ss")


def ask(question, options):
    if isinstance(options, tuple):
        answers = dict(zip(options, options))
    else:
        answers = options

    selection = None

    while selection not in answers:
        selection = raw_input(question)

    return answers.get(selection)


class RunAsAdmin(Task):
    def __init__(self, func, user, *args, **kwargs):
        super(RunAsAdmin, self).__init__(*args, **kwargs)
        self.func = func
        self.user = user
        self.mode = False if self.user == 'root' else True

    def run(self, *args, **kwargs):
        require('PROJECT')
        with settings(user=self.user, **{MODE_SUDO: self.mode}):
            return self.func(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)
