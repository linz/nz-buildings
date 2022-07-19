FROM postgis/postgis:14-3.2

ENV DEBIAN_FRONTEND noninteractive

RUN \
    apt-get update && \
    apt-get install -y "postgresql-$PG_MAJOR-pgtap" && \
    rm -rf /var/lib/apt/lists/*

COPY initialise-extensions.sql /docker-entrypoint-initdb.d/