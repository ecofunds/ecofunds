wget -O /tmp/uwsgi.tar.gz http://projects.unbit.it/downloads/uwsgi-1.2.3.tar.gz

mkdir /tmp/uwsgi
tar -C /tmp/uwsgi -zxvf /tmp/uwsgi.tar.gz
mv /tmp/uwsgi/uwsgi-1.2.3/* /tmp/uwsgi

make -C /tmp/uwsgi/
cp /tmp/uwsgi/uwsgi /usr/sbin/
rm -rf /tmp/uwsgi
rm -rf /tmp/uwsgi.tar.gz
