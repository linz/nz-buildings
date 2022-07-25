#!/bin/sh

docker exec qgis bash -c "cd /tests_directory && qgis_testrunner.sh buildings.tests.test_runner.run_test_modules"