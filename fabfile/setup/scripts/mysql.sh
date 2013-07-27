#Mysql5
password=`makepasswd --chars 32`
/bin/sh -c 'unset LC_ALL; LANG=pt_BR.UTF-8 DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get -q -y -o DPkg::Options::=--force-confold install mysql-server mysql-client libmysqlclient-dev'
/usr/bin/mysql -u root -D mysql -e "update user set password=password('$password') where user='root'"
/usr/bin/mysql -u root -e "flush privileges"
umask 077
cat > /root/.my.cnf <<EOF
[client]
user     = root
password = $password
EOF
