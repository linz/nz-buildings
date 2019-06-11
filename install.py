# coding=utf-8

import sys
import os
import psycopg2

from buildings.utilities import config

# Get the path for the parent directory of this file.
__location__ = os.path.dirname(os.path.realpath(__file__))

sys.path.append(__location__)

__version__ = "dev"

build = os.getenv("BUILD")

if build == "db":
    _host = "localhost"
    _port = os.getenv("PGPORT")
    _dbname = "nz-buildings-pgtap-db"
    _user = "travis"
    _pw = "travis"
else:
    from qgis.core import QgsApplication
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
    # Schema and Tables
    os.path.join("sql", "deploy", "buildings_reference", "schema_and_tables.sql"),
    os.path.join("sql", "deploy", "buildings_common", "schema_and_tables.sql"),
    os.path.join("sql", "deploy", "buildings", "schema_and_tables.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "schema_and_tables.sql"),
    os.path.join("sql", "deploy", "buildings_lds", "schema_and_tables.sql"),
    # Default Values
    os.path.join("sql", "deploy", "buildings_common", "default_values.sql"),
    os.path.join("sql", "deploy", "buildings", "default_values.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "default_values.sql"),
    # Views
    os.path.join("sql", "deploy", "buildings_bulk_load", "create_view_alter_relationships.sql"),
    # Functions
    os.path.join("sql", "deploy", "buildings_reference", "functions", "canal_polygons.sql"),
    os.path.join("sql", "deploy", "buildings_reference", "functions", "capture_source_area.sql"),
    os.path.join("sql", "deploy", "buildings_reference", "functions", "lagoon_polygons.sql"),
    os.path.join("sql", "deploy", "buildings_reference", "functions", "lake_polygons.sql"),
    os.path.join("sql", "deploy", "buildings_reference", "functions", "pond_polygons.sql"),
    os.path.join("sql", "deploy", "buildings_reference", "functions", "reference_update_log.sql"),
    os.path.join("sql", "deploy", "buildings_reference", "functions", "river_polygons.sql"),
    os.path.join("sql", "deploy", "buildings_reference", "functions", "suburb_locality.sql"),
    os.path.join("sql", "deploy", "buildings_reference", "functions", "swamp_polygons.sql"),
    os.path.join("sql", "deploy", "buildings_reference", "functions", "territorial_authority.sql"),
    os.path.join("sql", "deploy", "buildings_reference", "functions", "town_city.sql"),
    os.path.join("sql", "deploy", "buildings_common", "functions", "capture_method.sql"),
    os.path.join("sql", "deploy", "buildings_common", "functions", "capture_source_group.sql"),
    os.path.join("sql", "deploy", "buildings_common", "functions", "capture_source.sql"),
    os.path.join("sql", "deploy", "buildings", "functions", "lifecycle_stage.sql"),
    os.path.join("sql", "deploy", "buildings", "functions", "buildings.sql"),
    os.path.join("sql", "deploy", "buildings", "functions", "building_outlines.sql"),
    os.path.join("sql", "deploy", "buildings", "functions", "building_name.sql"),
    os.path.join("sql", "deploy", "buildings", "functions", "building_use.sql"),
    os.path.join("sql", "deploy", "buildings", "functions", "lifecycle.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "functions", "organisation.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "functions", "supplied_datasets.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "functions", "bulk_load_outlines.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "functions", "existing_subset_extracts.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "functions", "added.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "functions", "removed.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "functions", "related.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "functions", "matched.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "functions", "transferred.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "functions", "deletion_description.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "functions", "supplied_outlines.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "functions", "compare.sql"),
    os.path.join("sql", "deploy", "buildings_bulk_load", "functions", "load_to_production.sql"),
    os.path.join("sql", "deploy", "buildings_lds", "functions", "populate_buildings_lds.sql"),
]


def setup_connection():
    """ Sets up the DB Connection via psycopg2 """
    logindetails = "host={0} port={1} dbname={2} user={3} password={4}".format(
        _host, _port, _dbname, _user, _pw,
    )
    if type(logindetails) == str:
        conn = psycopg2.connect(logindetails)
    return conn


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

        if build == "db":
            script = os.path.join(__location__, "db", "tests", "testdata", "db", "buildings_reference.sql")
            cursor.execute(open(script, "r").read())
            print("DB_INSTALL: {} Loaded".format(script))

            script = os.path.join(__location__, "db", "tests", "testdata", "db", "buildings_common.sql")
            cursor.execute(open(script, "r").read())
            print("DB_INSTALL: {} Loaded".format(script))

            script = os.path.join(__location__, "db", "tests", "testdata", "db", "buildings.sql")
            cursor.execute(open(script, "r").read())
            print("DB_INSTALL: {} Loaded".format(script))

            script = os.path.join(__location__, "db", "tests", "testdata", "db", "buildings_bulk_load.sql")
            cursor.execute(open(script, "r").read())
            print("DB_INSTALL: {} Loaded".format(script))

            script = os.path.join(__location__, "db", "tests", "testdata", "db", "buildings_lds.sql")
            cursor.execute(open(script, "r").read())
            print("DB_INSTALL: {} Loaded".format(script))

            script = os.path.join(__location__, "db", "tests", "testdata", "update_sequences_pgtap_db.sql")
            cursor.execute(open(script, "r").read())
            print("DB_INSTALL: {} Loaded".format(script))

        else:
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
    db_install()


if __name__ == "__main__":
    main()
