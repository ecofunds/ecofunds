#################
# Validate Args #
#################
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 FQDN EMAIL"
    exit 1
fi


# Postfix
SERVER_FQDN="$1"
SERVER_EMAIL="$2"

cat > /var/cache/debconf/postfix.preseed <<EOF
postfix postfix/chattr  boolean false
postfix postfix/destinations    string  $SERVER_FQDN
postfix postfix/mailbox_limit   string  0
postfix postfix/mailname    string  $SERVER_FQDN
postfix postfix/main_mailer_type    select  Internet Site
postfix postfix/mynetworks  string  127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
postfix postfix/protocols   select  all
postfix postfix/recipient_delim string  +
postfix postfix/root_address    string  $SERVER_EMAIL
EOF

if [ ! -d /etc/postfix ]
then
    mkdir -p /etc/postfix
fi

cat > /etc/postfix/main.cf <<EOF
# See /usr/share/postfix/main.cf.dist for a commented, more complete version


# Debian specific:  Specifying a file name will cause the first
# line of that file to be used as the name.  The Debian default
# is /etc/mailname.
#myorigin = /etc/mailname

smtpd_banner = $myhostname ESMTP $mail_name (Ubuntu)
biff = no

# appending .domain is the MUA's job.
append_dot_mydomain = no

# Uncomment the next line to generate "delayed mail" warnings
#delay_warning_time = 4h

readme_directory = no

# TLS parameters
smtpd_tls_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
smtpd_tls_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
smtpd_use_tls=yes
smtpd_tls_session_cache_database = btree:${data_directory}/smtpd_scache
smtp_tls_session_cache_database = btree:${data_directory}/smtp_scache

# See /usr/share/doc/postfix/TLS_README.gz in the postfix-doc package for
# information on enabling SSL in the smtp client.

myhostname = $SERVER_FQDN
alias_maps = hash:/etc/aliases
alias_database = hash:/etc/aliases
myorigin = /etc/mailname
mydestination = $SERVER_FQDN, localhost
relayhost =
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
mailbox_size_limit = 0
recipient_delimiter = +
inet_interfaces = loopback-only
inet_protocols = all

EOF

debconf-set-selections /var/cache/debconf/postfix.preseed
apt-get -q -y -o DPkg::Options::=--force-confold install postfix
apt-get -q -y install mailutils
