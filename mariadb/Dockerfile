FROM debian:latest
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y --no-install-recommends \
        mariadb-server-10.0 \
        percona-xtrabackup \
        socat \
        expect \
        sudo \
    && apt-get clean \
    && rm -rf /var/lib/mysql/* \
    && mkdir -p /opt/bin \
    && mkdir -p /var/run/mysqld

COPY mariadb_sudoers /etc/sudoers.d/mariadb_sudoers
COPY mariadb-security-reset.expect /opt/bin/mariadb-security-reset.expect
COPY my.cnf /etc/mysql/my.cnf
COPY entrypoint.sh /opt/bin/entrypoint.sh
RUN chmod 750 /etc/sudoers.d \
    && chmod 440 /etc/sudoers.d/mariadb_sudoers \
    && usermod -a -G mysql mysql \
    && chown -R mysql: /etc/mysql /var/lib/mysql /var/run/mysqld \
    && chmod 0777 /opt/bin/entrypoint.sh \
    && chmod 0777 /opt/bin/mariadb-security-reset.expect

USER mysql
ENTRYPOINT /opt/bin/entrypoint.sh

