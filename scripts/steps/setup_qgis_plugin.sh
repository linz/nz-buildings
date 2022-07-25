#!/bin/sh

PROFILE_DIR=/root/.local/share/QGIS/QGIS3/profiles/default

docker exec qgis mkdir -p $PROFILE_DIR/buildings
docker exec qgis cp /tests_directory/buildings/tests/pg_config_test.ini $PROFILE_DIR/buildings/pg_config.ini
# docker exec qgis ln -s /tests_directory/buildings $PROFILE_DIR/python/plugins/buildings
docker exec qgis qgis_setup.sh buildings
