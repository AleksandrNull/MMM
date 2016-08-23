#!/bin/bash -e

DB_ROOT_PASSWORD=swordfish

function bootstrap_db {
    #mysqld_safe --wsrep-new-cluster --defaults-file=/etc/mysql/my.cnf &
    mysqld_safe &
    echo "Wait for the mariadb server to be ready before starting the security reset"
    TIMEOUT=${DB_MAX_TIMEOUT:-60}
    while [[ ! -f /var/lib/mysql/mariadb.pid ]]; do
        if [[ ${TIMEOUT} -gt 0 ]]; then
            let TIMEOUT-=1
            sleep 1
        else
            echo "Mariadb failed to start. Waited for $DB_MAX_TIMEOUT seconds."
            exit 1
        fi
    done
    echo "Running a mysql_security_reset"
    cd /tmp && /opt/bin/mariadb-security-reset.expect ${DB_ROOT_PASSWORD}
    echo "Running mysql grant privileges commands"
    mysql -u root --password="${DB_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PASSWORD}' WITH GRANT OPTION;"
    mysql -u root --password="${DB_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '${DB_ROOT_PASSWORD}' WITH GRANT OPTION;"
    echo "Shuting down mariadb"
    mysqladmin -uroot -p"${DB_ROOT_PASSWORD}" shutdown
    wait $(jobs -p)
}

function bootstrap {
    if [[ $(stat -c %U:%G /var/lib/mysql) != "mysql:mysql" ]]; then
        sudo chown mysql: /var/lib/mysql
    fi
    mysql_install_db
    bootstrap_db
    touch /tmp/mariadb_ok
}

function server {
    while true
    do
      mysqld
    done
}

#test -f /tmp/mariadb_ok && nc -z {{ network_topology["private"]["address"] }} {{ mariadb_port }}

[[ -f /tmp/mariadb_ok ]] || bootstrap
[[ -f /tmp/mariadb_ok ]] && server
