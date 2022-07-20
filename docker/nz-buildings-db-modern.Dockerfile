FROM postgis/postgis:14-3.2

LABEL version="v1"

ENV SQITCH_VERSION 1.2.1
ENV DEBIAN_FRONTEND noninteractive

RUN \
    apt-get update && \
    apt-get install -y \
        "postgresql-$PG_MAJOR-pgtap" \
        perl \
        build-essential \
        cpanminus && \
    rm -rf /var/lib/apt/lists/* && \
    cpanm --notest --no-interactive --no-man-pages "DWHEELER/App-Sqitch-v$SQITCH_VERSION.tar.gz" && \
    rm -r ~/.cpanm && \
    apt-get purge -y \
        build-essential \
        cpanminus && \
    apt-get autoremove -y

COPY initialise-extensions.sql /docker-entrypoint-initdb.d/