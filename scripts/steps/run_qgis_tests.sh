#!/bin/sh

echo >&2 ""
echo >&2 "######################"
echo >&2 "# Running QGIS tests #"
echo >&2 "######################"
echo >&2 ""

docker exec \
--env QGIS_TEST_MODULE=$QGIS_TEST_MODULE \
--env QGIS_TEST_CLASS=$QGIS_TEST_CLASS \
--env QGIS_TEST_NAME=$QGIS_TEST_NAME \
--workdir /tests_directory \
qgis \
bash buildings/tests/run.sh
