# Adapted from unmaintained PostgreSQL 9.3 Dockerfile
# https://github.com/docker-library/postgres/blob/69bc540ecfffecce72d49fa7e4a46680350037f9/9.3/Dockerfile
# Changed to use archive PostgreSQL apt repo which now hosts older versions,
# and to install additional dependencies we want of PostGIS, Sqitch, and pgTAP

FROM ubuntu:trusty

LABEL version="v1"

ENV LANG en_US.utf8

ENV POSTGRESQL_VERSION 9.3
ENV POSTGIS_VERSION 2.3
ENV GOSU_VERSION 1.14
ENV SQITCH_VERSION 1.2.1
ENV DEBIAN_FRONTEND noninteractive

# explicitly set user/group IDs
RUN groupadd -r postgres --gid=999 && useradd -r -g postgres --uid=999 postgres

# Hack to appease the docker gods: https://stackoverflow.com/a/48782486
RUN printf '#!/bin/sh\nexit 0' > /usr/sbin/policy-rc.d

# Make the "en_US.UTF-8" locale so postgres will be utf-8 enabled by default
RUN \
    apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/* && \
    localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

# Install dependencies for adding repositories and directly downloading dependencies
RUN \
    apt-get update && \
    apt-get install -y curl ca-certificates gnupg && \
    rm -rf /var/lib/apt/lists/*

# Fix expired certificate used by Lets Encrypt
RUN \
    sed -i 's|mozilla/DST_Root_CA_X3.crt|!mozilla//DST_Root_CA_X3.crt|g' /etc/ca-certificates.conf && \
    dpkg-reconfigure -fnoninteractive ca-certificates

# Install gosu
RUN \
    curl -LsS -o /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" && \
#     curl -o /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture).asc" && \
#     export GNUPGHOME="$(mktemp -d)"  && \
#     gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 && \
#     gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu && \
#     rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc && \
    chmod +x /usr/local/bin/gosu && \
    gosu nobody true

# Add the postgres repo
RUN \
    curl -LsS https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
    gpg --dearmor | \
    tee /etc/apt/trusted.gpg.d/apt.postgresql.org.gpg >/dev/null && \
    echo 'deb https://apt-archive.postgresql.org/pub/repos/apt trusty-pgdg-archive main' > /etc/apt/sources.list.d/pgdg.list

# Install packages
RUN \
    apt-get update && \
    apt-get install -y postgresql-common && \
    sed -ri 's/#(create_main_cluster) .*$/\1 = false/' /etc/postgresql-common/createcluster.conf  && \
    apt-get install -y \
        "postgresql-$POSTGRESQL_VERSION" \
        "postgresql-$POSTGRESQL_VERSION-pgtap" \
        "postgresql-$POSTGRESQL_VERSION-postgis-$POSTGIS_VERSION" \
        "postgresql-$POSTGRESQL_VERSION-postgis-$POSTGIS_VERSION-scripts" \
        perl \
        build-essential \
        cpanminus && \
    rm -rf /var/lib/apt/lists/* && \
    cpanm --notest --no-interactive --no-man-pages "DWHEELER/App-Sqitch-v$SQITCH_VERSION.tar.gz" && \
    rm -r ~/.cpanm && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y

# make the sample config easier to munge (and "correct by default")
RUN \
    mv -v /usr/share/postgresql/$POSTGRESQL_VERSION/postgresql.conf.sample /usr/share/postgresql/ && \
    ln -sv ../postgresql.conf.sample /usr/share/postgresql/$POSTGRESQL_VERSION/ && \
    sed -ri "s!^#?(listen_addresses)\s*=\s*\S+.*!\1 = '*'!" /usr/share/postgresql/postgresql.conf.sample

RUN \
    mkdir -p /var/run/postgresql && \
    chown -R postgres /var/run/postgresql && \
    mkdir /docker-entrypoint-initdb.d && \
    chown -R postgres /docker-entrypoint-initdb.d

ENV PATH /usr/lib/postgresql/$POSTGRESQL_VERSION/bin:$PATH
ENV PGDATA /var/lib/postgresql/data
VOLUME /var/lib/postgresql/data

COPY nz-buildings-db-legacy-entrypoint.sh /
RUN chown -R postgres /nz-buildings-db-legacy-entrypoint.sh && chmod +x /nz-buildings-db-legacy-entrypoint.sh
COPY initialise-extensions.sql /docker-entrypoint-initdb.d/

ENTRYPOINT ["/nz-buildings-db-legacy-entrypoint.sh"]

EXPOSE 5432
CMD ["postgres"]
