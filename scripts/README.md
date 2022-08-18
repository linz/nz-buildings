# NZ Buildings scripts

This directory contains scripts to automated development, testing, and maintenance tasks.

Each script is a bash shell script, tested on Ubuntu, but which should run on any \*nix system.

Files in the [steps](./steps) subdirectory are called by the scripts in this directory (as well as the github actions configuration). They may access environment variables expected to be set by either the calling script or the github actions configuration, and so may not work when called directly unless those required environment variables are set manually.

## [bump_version.sh](./bump_version.sh)

Updates the version number in the QGIS plugin metadata and changelog for creating a release. Called with the desired version number as a single argument, e.g.:

```bash
./bump_version.sh 0.1
```

## [dump_schema.sh](./dump_schema.sh)

Used for dumping the contents of a test database to files for use in test data. Has not been updated to account for changes to dockerise test running, and simply moved to this drectory verbatim. Will need some changes to run, but is included for reference and as a starting point if test data needs to be updated in the future.

## [run_db_tests.sh](./run_db_tests.sh)

Runs the pgTAP tests from [db/tests](../db/tests/) in a PostgreSQL database running in a docker container.

By default the ["Legacy" PostgreSQL docker image](../docker/nz-buildings-db-legacy.Dockerfile) is used. To use the ["Modern" PostgreSQL docker image](../docker/nz-buildings-db-modern.Dockerfile), set the environment variable `DB_VERSION` to `modern`.

## [run_qgis_tests.sh](./run_qgis_tests.sh)

Runs the QGIS unit tests, using a PostgreSQL database running in a docker container alongside an instance of QGIS running in a second docker container.

The script takes three optional arguments to run only a subset of tests, e.g.:

```bash
./run_qgis_tests.sh <test_module> <test_class> <test_method>
```

- `<test_module>` is a python module (in dot notation) containing the tests to be run (e.g. `buildings.tests.gui.test_processes_add_bulk_load`)
- `<test_class>` is a test class inside that module (e.g. `ProcessBulkAddOutlinesTest`)
- `<test_method>` is a method of the specified test class (e.g. `test_ui_on_geometry_drawn`)

The script can be called with no arguments to run the entire test suite, one argument to run all tests in a specified module, two arguments to run all tests in a specified class within that module, and three arguments to run a single test method of the specified class in the specified module.

By default a docker image with QGIS version 3.16 is used. To use a different version, set the environment variable `QGIS_VERSION` to the desired version, e.g. `3_10` or `3_24`. The value corresponds to the version number of the "release" QGIS docker images, [possible values for which can be seen on Docker Hub](https://hub.docker.com/r/qgis/qgis/tags?page=1&name=release), with `QGIS_VERSION` needing to be set to the numeric portion of the image name.

By default the ["Legacy" PostgreSQL docker image](../docker/nz-buildings-db-legacy.Dockerfile) is used. To use the ["Modern" PostgreSQL docker image](../docker/nz-buildings-db-modern.Dockerfile), set the environment variable `DB_VERSION` to `modern`.

By default QGIS is run without the GUI being visible on screen. To see the GUI window and watch tests being run, set the environment variable `QGIS_DISPLAY` to the same value as the environment variable `DISPLAY`.

## [run_qgis_interactively.sh](./run_qgis_tests.sh)

Runs QGIS interactively inside a docker container.

By default a docker image with QGIS version 3.16 is used. To use a different version, set the environment variable `QGIS_VERSION` to the desired version, e.g. `3_10` or `3_24`. The value corresponds to the version number of the "release" QGIS docker images, [possible values for which can be seen on Docker Hub](https://hub.docker.com/r/qgis/qgis/tags?page=1&name=release), with `QGIS_VERSION` needing to be set to the numeric portion of the image name.

By default the ["Legacy" PostgreSQL docker image](../docker/nz-buildings-db-legacy.Dockerfile) is used. To use the ["Modern" PostgreSQL docker image](../docker/nz-buildings-db-modern.Dockerfile), set the environment variable `DB_VERSION` to `modern`.