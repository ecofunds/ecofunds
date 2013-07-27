#!/bin/bash

# Postgres
apt-get -y -q install postgresql-9.1
apt-get -y -q install postgresql-client-9.1
apt-get -y -q install postgresql-contrib-9.1
apt-get -y -q install libpq-dev

# http://jacobian.org/writing/pg-encoding-ubuntu/
sudo -u postgres pg_dropcluster --stop 9.1 main
sudo -u postgres pg_createcluster --start -e UTF-8 9.1 main

# Configuração para psql permitir dump
cp pg_hba.conf /etc/postgresql/9.1/main/pg_hba.conf
/etc/init.d/postgresql-9.1 restart
