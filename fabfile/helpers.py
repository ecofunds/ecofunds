# coding: utf-8
from datetime import datetime
from fabric.api import env


class Project(dict):
    """
    Describes the remote directory structure for a project.
    """
    def __init__(self, basedir, instance, project, package):
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


def make_environment(name, domain, user=None):
    """
    Configure Fabric's environment according our conventions.
    """
    project = domain.partition('.')[0]
    cname = '%s.%s' % (name, domain)
    env.user = user or project
    env.hosts = [cname]
    env.settings = '%s.settings' % project
    env.PROJECT = Project('~', cname, project)


def ask(question, options):
    if isinstance(options, tuple):
        answers = dict(zip(options, options))
    else:
        answers = options

    selection = None

    while selection not in answers:
        selection = raw_input(question)

    return answers.get(selection)
