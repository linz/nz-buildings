#!/bin/sh

echo >&2 ""
echo >&2 "######################"
echo >&2 "# Running QGIS tests #"
echo >&2 "######################"
echo >&2 ""

docker exec qgis bash -c "cd /tests_directory && qgis_testrunner.sh buildings.tests.test_runner.run_test_modules"