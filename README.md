![NZ Buildings](./media/header.png)

[![CI Status](https://github.com/linz/nz-buildings/actions/workflows/build.yml/badge.svg)](https://github.com/linz/nz-buildings/actions/workflows/build.yml) [![Documentation Status](https://readthedocs.org/projects/nz-buildings/badge/?version=latest)](https://nz-buildings.readthedocs.io/en/latest/introduction.html) [![Latest Release](https://badgen.net/github/release/linz/nz-buildings?label=Release&labelColor=2e3a44&color=5cc3db)](https://github.com/linz/nz-buildings/releases) [![Current Building Outlines Feature Count](https://badgen.net/badge/Total%20Buildings/3%2C320%2C498?labelColor=2e3a44&color=5cc3db)](https://data.linz.govt.nz/layer/101290) [![License](https://badgen.net/badge/License/BSD%203-clause?labelColor=2e3a44&color=blue)](https://github.com/linz/nz-buildings/blob/master/LICENSE) [![Convetional Commits](https://badgen.net/badge/Commits/conventional?labelColor=2e3a44&color=EC5772)](https://conventionalcommits.org) [![Code Style](https://badgen.net/badge/Code%20Style/black?labelColor=2e3a44&color=000000)](https://github.com/psf/black)


# NZ Buildings

The *NZ Buildings* system is used by [Toitū Te Whenua Land Information New Zealand](https://www.linz.govt.nz/)to manage New Zealand's national building outlines dataset. This dataset is published under CC-BY-4.0 [on the LINZ Data Service](https://data.linz.govt.nz/layer/101290). Documentation of the dataset itself is available in the [NZ Building Outlines Data Dictionary](https://nz-buildings.readthedocs.io/en/latest/introduction.html).


## Features

The Topography team at Toitū Te Whenua LINZ built this system and use it to:

- validate building outlines captured via feature extraction
- assign additional attributes (capture metadata, administrative boundaries)
- manually add, modify or delete building outlines where required
- compare a new set of building outlines against existing building outlines and categorise matching, added, removed or related buildings
- manage the lifecycle of building outlines across multiple data captures
- prepare data to be published on the LINZ Data Service


## Components

- [PostgreSQL](https://www.postgresql.org/)/[PostGIS](https://postgis.net/) database schema for data storage
- [QGIS](https://qgis.org/) plugin for data maintenance
- [data dictionary](https://nz-buildings.readthedocs.io/en/latest/introduction.html) hosted on readthedocs
- [ISO 19115 geospatial metadata](./metadata) to accompany the published datasets
- [Dockerfiles](./docker) of specific PostgreSQL versions and dependencies used for testing.

All of the components build upon other free and open source software. See [ACKNOWLEDGEMENTS.md](./ACKNOWLEDGEMENTS.md) for a summary.


## License

This system is under the 3-clause BSD License, except where otherwise specified. See the [LICENSE](./LICENSE) file for more details.


## Database

The database for the *NZ Buildings* system is a PostgreSQL database with the PostGIS database extension for handling geographic objects.

### Dependencies

- [PostgreSQL](https://www.postgresql.org/) database with [PostGIS](https://postgis.net/) extension. Tested versions are PostgreSQL 9.3 with PostGIS 2.3, and PostgreSQL 14 with PostGIS 3.2.
- [Sqitch](https://sqitch.org/) is used for database schema migrations.
- [pgTAP](https://pgtap.org/) is used for database testing. This is included inside the Dockerfiles used for automated testing.
- [Docker](https://www.docker.com/) is used for automated testing, of both QGIS plugin unit tests, and database tests using pgTAP.

### Development and testing

For development and testing, a copy of the database including test data can be run in a docker container. See the scripts in the [scripts](./scripts) directory and the README there for further information.


## QGIS plugin

### Dependencies

The QGIS plugin is tested in QGIS versions 3.10, 3.16, and 3.24.

### Installation

First clone this repository:

```shell
git clone https://github.com/linz/nz-buildings.git
```

Then, from the repository directory, create a symantic link from the `buildings` folder which contains the QGIS plugin to your local QGIS profile directory. On Ubuntu this will be:

```shell
ln -s "$(pwd)/buildings" ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

Then create a database config file for the plugin. If using Docker to run the database locally, you can use the testing config file as-is, otherwise you can use it as a base and edit the required details as needed.

```shell
cp ./buildings/tests/pg_config_tests.ini ~/.local/share/QGIS/QGIS3/profiles/default/buildings/pg_config.ini
```

### Development and testing

Scripts are provided to run Python unit tests in QGIS in a docker container. See the README in the [scripts](./scripts) directory for more information on [run_qgis_tests.sh](./scripts/run_qgis_tests.sh) and [run_qgis_interactively.sh](./scripts/run_qgis_interactively.sh).
