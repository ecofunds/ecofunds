# -*- encoding: utf-8 -*-
from unipath import Path
from ..helpers import timestamp, RunAsAdmin
from fabric.api import run, env, put, sudo, get, task, puts
from fabric.colors import yellow


@task(task_class=RunAsAdmin, user=env.local_user)
def create(dbuser, dbname):
    """
    Create a Mysql Database and User: db.mysql.create:dbuser,dbname

    Example: db.mysql.create:myproject,myproject

    The password will be randomly generated.
    *  Run once.
    ** This command must be executed by a sudoer.
    """
    password = run('makepasswd --chars 32')
    assert(len(password) == 32)  # Ouch!

    sudo("mysql --defaults-file=/root/.my.cnf -e \"CREATE DATABASE %(dbname)s;\"" % locals())

    sudo("mysql --defaults-file=/root/.my.cnf -e \"CREATE USER '%(dbuser)s'@'localhost' IDENTIFIED BY '%(password)s';\"" % locals())
    sudo("mysql --defaults-file=/root/.my.cnf -e \"GRANT ALL PRIVILEGES ON %(dbname)s.* TO '%(dbuser)s'@'localhost';\"" % locals())

    # Persist database password
    my_cfg = "[client]\ndatabase=%s\nuser=%s\npassword=%s" % (dbname, dbuser, password)
    sudo("echo '%s' > %s/.my.cnf" % (my_cfg, env.PROJECT.share))
    sudo('chmod 640 %(share)s/.my.cnf' % env.PROJECT)
    sudo('chown %(user)s %(share)s/.my.cnf' % env.PROJECT)
    sudo('chgrp www-data %(share)s/.my.cnf' % env.PROJECT)

    db_url = 'mysql://%(dbuser)s:%(password)s@localhost/%(dbname)s' % locals()
    puts(yellow('DATABASE_URL => ' + db_url))
    return db_url


@task(task_class=RunAsAdmin, user=env.local_user)
def drop(dbuser, dbname):
    """
    Drop a Mysql Database and User: db.mysql.drop:dbuser,dbname

    Example: db.mysql.drop:myproject,myproject

    *  Run once.
    ** This command must be executed by a sudoer.
    """
    sudo("mysql --defaults-file=/root/.my.cnf -e \"DROP DATABASE %(dbname)s;\"" % locals())
    sudo("mysql --defaults-file=/root/.my.cnf -e \"DROP USER '%(dbuser)s'@'localhost';\"" % locals())
    sudo('rm %(share)s/.my.cnf' % env.PROJECT)


@task(task_class=RunAsAdmin, user=env.local_user)
def backup(dbname):
    '''
    Get dump from server MySQL database

    Usage: fab db.mysql.backup
    '''
    remote_dbfile = '%(tmp)s/db-%(instance)s-%(project)s-' % env.PROJECT + timestamp() +'.sql.bz2'
    sudo('mysqldump --defaults-extra-file=/root/.my.cnf --default-character-set=utf8 -R -c --lock-tables=FALSE %(dbname)s | bzip2 -c  > %(remote_dbfile)s' % locals())
    get(remote_dbfile, '.')

    #remove the temporary remote dump file
    sudo('rm ' + remote_dbfile)


@task(task_class=RunAsAdmin, user=env.local_user)
def restore(dbname, local_file):
    '''
    Restore a MySQL dump into dbname.

    Usage: fab db.mysql.backup
    '''
    local_file = Path(local_file).absolute()

    remote_file = Path(put(local_file, env.PROJECT.tmp, use_sudo=True)[0])

    if remote_file.endswith('.bz2'):
        sudo('bunzip2 ' + remote_file)
        remote_file = remote_file.parent.child(remote_file.stem)

    sudo('mysql --defaults-extra-file=/root/.my.cnf -e "DROP DATABASE %(dbname)s; CREATE DATABASE %(dbname)s;"' % locals())
    sudo('mysql --defaults-extra-file=/root/.my.cnf %(dbname)s < %(remote_file)s' % locals())

    # cleanup
    sudo('rm ' + remote_file)
