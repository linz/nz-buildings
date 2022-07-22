#!/bin/sh

export PGHOST=localhost
export PGPORT=5432
export PGUSER=buildings
export PGPASSWORD=buildings
export SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # Directory this file is in
export BASE_DIR="${SCRIPTS_DIR%/*}"  # Parent directory of $SCRIPTS_DIR
export DB_DOCKER_IMAGE="ghcr.io/linz/nz-buildings-db-legacy:v1"

bash $SCRIPTS_DIR/steps/launch_db_container.sh
