# coding=utf-8

import sys
import os
import psycopg2

from qgis.core import QgsDataSourceURI, QgsApplication
from buildings.utilities import config

# Get the path for the parent directory of this file.
__location__ = os.path.dirname(os.path.realpath(__file__))

sys.path.append(__location__)

__version__ = "dev"

app = QgsApplication([], True)
QgsApplication.initQgis()
config_path = os.path.join(
    QgsApplication.qgisSettingsDirPath(), "buildings", "pg_config.ini"
)

pg_config = config.read_config_file(config_path)
_host = pg_config["localhost"]["host"]
_port = pg_config["localhost"]["port"]
_dbname = pg_config["localhost"]["dbname"]
_user = pg_config["localhost"]["user"]
_pw = pg_config["localhost"]["password"]

SQL_SCRIPTS = [
    os.path.join("sql", "buildings_reference", "01-create-schema-and-tables.sql"),
    os.path.join("sql", "buildings_common", "01-create-schema-and-tables.sql"),
    os.path.join("sql", "buildings", "01-create-schema-and-tables.sql"),
    os.path.join("sql", "buildings_bulk_load", "01-create-schema-and-tables.sql"),
    os.path.join("sql", "buildings_lds", "01-create-schema-and-tables.sql"),
    # os.path.join("sql", "buildings_reference", "02-default-values.sql"),
    os.path.join("sql", "buildings_common", "02-default-values.sql"),
    os.path.join("sql", "buildings", "02-default-values.sql"),
    os.path.join("sql", "buildings_bulk_load", "02-default-values.sql"),
    # os.path.join("sql", "buildings_lds", "02-default-values.sql"),
    os.path.join("sql", "buildings_bulk_load", "03-alter_relationships_create_view.sql"),
    os.path.join("sql", "01-buildings_version.sql"),
    os.path.join("sql", "buildings_reference", "functions", "01-canal_polygons.sql"),
    os.path.join("sql", "buildings_reference", "functions", "02-capture_source_area.sql"),
    os.path.join("sql", "buildings_reference", "functions", "03-lagoon_polygons.sql"),
    os.path.join("sql", "buildings_reference", "functions", "04-lake_polygons.sql"),
    os.path.join("sql", "buildings_reference", "functions", "05-pond_polygons.sql"),
    os.path.join("sql", "buildings_reference", "functions", "06-reference_update_log.sql"),
    os.path.join("sql", "buildings_reference", "functions", "07-river_polygons.sql"),
    os.path.join("sql", "buildings_reference", "functions", "08-suburb_locality.sql"),
    os.path.join("sql", "buildings_reference", "functions", "09-swamp_polygons.sql"),
    os.path.join("sql", "buildings_reference", "functions", "10-territorial_authority_and_territorial_authority_grid.sql"),
    os.path.join("sql", "buildings_reference", "functions", "11-town_city.sql"),
    os.path.join("sql", "buildings_common", "functions", "01-capture_method.sql"),
    os.path.join("sql", "buildings_common", "functions", "02-capture_source_group.sql"),
    os.path.join("sql", "buildings_common", "functions", "03-capture_source.sql"),
    os.path.join("sql", "buildings", "functions", "01-lifecycle_stage.sql"),
    # os.path.join("sql", "buildings", "functions", "02-use.sql"),
    os.path.join("sql", "buildings", "functions", "03-buildings.sql"),
    os.path.join("sql", "buildings", "functions", "04-building_outlines.sql"),
    # os.path.join("sql", "buildings", "functions", "05-building_name.sql"),
    # os.path.join("sql", "buildings", "functions", "06-building_use.sql"),
    os.path.join("sql", "buildings", "functions", "07-lifecycle.sql"),
    os.path.join("sql", "buildings_bulk_load", "functions", "01-organisation.sql"),
    # os.path.join("sql", "buildings_bulk_load","functions", "02-bulk_load_status.sql"),
    # os.path.join("sql", "buildings_bulk_load","functions", "03-qa_status.sql"),
    os.path.join("sql", "buildings_bulk_load", "functions", "04-supplied_datasets.sql"),
    os.path.join("sql", "buildings_bulk_load", "functions", "05-bulk_load_outlines.sql"),
    os.path.join("sql", "buildings_bulk_load", "functions", "06-existing_subset_extracts.sql"),
    os.path.join("sql", "buildings_bulk_load", "functions", "07-added.sql"),
    os.path.join("sql", "buildings_bulk_load", "functions", "08-removed.sql"),
    os.path.join("sql", "buildings_bulk_load", "functions", "09-related.sql"),
    os.path.join("sql", "buildings_bulk_load", "functions", "10-matched.sql"),
    os.path.join("sql", "buildings_bulk_load", "functions", "11-transferred.sql"),
    os.path.join("sql", "buildings_bulk_load", "functions", "12-deletion_description.sql"),
    os.path.join("sql", "buildings_bulk_load", "functions", "13-supplied_outlines.sql"),
    os.path.join("sql", "buildings_bulk_load", "functions", "14-compare_buildings.sql"),
    # os.path.join("sql", "buildings_lds","functions", "01-nz_building_outlines.sql"),
    # os.path.join("sql", "buildings_lds","functions", "02-nz_building_outlines_all_sources.sql"),
    # os.path.join("sql", "buildings_lds","functions", "03-nz_building_outlines_lifecycle.sql"),
    os.path.join("sql", "buildings_lds", "functions", "04-load_buildings.sql"),
    os.path.join("sql", "buildings_lds", "functions", "05-populate_buildings_lds.sql"),
]

BUILD_SCRIPTS = [
    os.path.join("sql", "01-buildings_version.sql.in")
]


def setup_connection():
    """ Sets up the DB Connection via psycopg2 """
    logindetails = "host={0} port={1} dbname={2} user={3} password={4}".format(
        _host, _port, _dbname, _user, _pw,
    )
    if type(logindetails) == str:
        conn = psycopg2.connect(logindetails)
    return conn


def build_scripts():
    for script in BUILD_SCRIPTS:
        script = os.path.join(__location__, "db", script)
        with open(script) as f:
            with open(script.replace(".sql.in", ".sql"), "w") as f1:
                for line in f:
                    if "@@VERSION@@" in line:
                        f1.write(line.replace("@@VERSION@@", __version__))
                    else:
                        f1.write(line)


def db_install():
    try:
        cursor.execute("DROP SCHEMA IF EXISTS buildings_lds CASCADE;")
        cursor.execute("DROP SCHEMA IF EXISTS buildings_bulk_load CASCADE;")
        cursor.execute("DROP SCHEMA IF EXISTS buildings CASCADE;")
        cursor.execute("DROP SCHEMA IF EXISTS buildings_common CASCADE;")
        cursor.execute("DROP SCHEMA IF EXISTS buildings_reference CASCADE;")

        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis SCHEMA public;")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS intarray SCHEMA public;")
        cursor.execute("SET client_min_messages TO WARNING;")

        script = os.path.join(__location__, "db", "tests", "testdata", "create_test_admin_bdys_schema.sql")
        cursor.execute(open(script, "r").read())
        print("DB_INSTALL: {} Loaded".format(script))

        script = os.path.join(__location__, "db", "tests", "testdata", "plugin", "admin_bdys.sql")
        cursor.execute(open(script, "r").read())
        print("DB_INSTALL: {} Loaded".format(script))

        script = os.path.join(__location__, "db", "tests", "testdata", "create_test_aerial_schema.sql")
        cursor.execute(open(script, "r").read())
        print("DB_INSTALL: {} Loaded".format(script))

        script = os.path.join(__location__, "db", "tests", "testdata", "plugin", "aerial_lds.sql")
        cursor.execute(open(script, "r").read())
        print("DB_INSTALL: {} Loaded".format(script))

        for script in SQL_SCRIPTS:
            script = os.path.join(__location__, "db", script)
            cursor.execute(open(script, "r").read())
            print("DB_INSTALL: {} Loaded".format(script))

        script = os.path.join(__location__, "db", "tests", "testdata", "01-insert_test_data_reference.sql")
        cursor.execute(open(script, "r").read())
        print("DB_INSTALL: {} Loaded".format(script))

        script = os.path.join(__location__, "db", "tests", "testdata", "06-insert_test_data_buildings_bulk_load_plugin.sql")
        cursor.execute(open(script, "r").read())
        print("DB_INSTALL: {} Loaded".format(script))

        cursor.execute("SELECT buildings_bulk_load.compare_building_outlines(2);")

        connection.commit()
        cursor.close()
        connection.close()

    except psycopg2.DataError, exception:
        print(exception)
        connection.rollback()
        connection.close()


def main():
    global connection
    connection = setup_connection()
    global cursor
    cursor = connection.cursor()
    build_scripts()
    db_install()


if __name__ == "__main__":
    main()
