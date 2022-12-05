#!/bin/sh

echo >&2 ""
echo >&2 "##########################"
echo >&2 "# Setting up QGIS plugin #"
echo >&2 "##########################"
echo >&2 ""

PROFILE_DIR=/root/.local/share/QGIS/QGIS3/profiles/default

docker exec qgis mkdir -p $PROFILE_DIR/buildings
docker exec qgis cp /tests_directory/buildings/tests/config.ini $PROFILE_DIR/buildings/config.ini
docker exec qgis qgis_setup.sh buildings
