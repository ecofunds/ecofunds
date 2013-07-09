#!/bin/bash
set -eux

#Postgres
apt-get -y -q install postgresql-9.1
apt-get -y -q install postgresql-client-9.1
apt-get -y -q install postgresql-contrib-9.1
apt-get -y -q install libpq-dev

pip install psycopg2
