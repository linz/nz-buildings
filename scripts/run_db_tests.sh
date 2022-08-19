#!/bin/sh

export DB_VERSION=${DB_VERSION:-'legacy'}

export PGHOST=localhost
export PGPORT=54320
export PGUSER=buildings
export PGPASSWORD=buildings
export SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # Directory this file is in
export BASE_DIR="${SCRIPTS_DIR%/*}"  # Parent directory of $SCRIPTS_DIR
export DB_DOCKER_IMAGE="ghcr.io/linz/nz-buildings-db-$DB_VERSION:v1"
export DOCKER_NETWORK=buildings

bash $SCRIPTS_DIR/steps/create_docker_network.sh &&
bash $SCRIPTS_DIR/steps/launch_database_container.sh &&
bash $SCRIPTS_DIR/steps/load_additional_schemas.sh &&
bash $SCRIPTS_DIR/steps/sqitch_deploy_verify.sh &&
bash $SCRIPTS_DIR/steps/sqitch_revert.sh &&
bash $SCRIPTS_DIR/steps/sqitch_deploy.sh &&
bash $SCRIPTS_DIR/steps/load_db_test_data.sh &&
bash $SCRIPTS_DIR/steps/run_pgtap_tests.sh ;
bash $SCRIPTS_DIR/steps/cleanup.sh
