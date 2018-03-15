import os
import psycopg2

from qgis.core import QgsApplication

import config
# from warnings import roads_warning
# from roads_logging import Logger, TEST_SQL_FUNCTIONS

config_path = os.path.join(
    QgsApplication.qgisSettingsDirPath(), "buildings", "pg_config.ini"
)
pg_config = config.read_config_file(config_path)
_host = pg_config["localhost"]["host"]
_port = pg_config["localhost"]["port"]
_dbname = pg_config["localhost"]["dbname"]
_user = pg_config["localhost"]["user"]
_pw = pg_config["localhost"]["password"]

_open_cursor = None

try:
    _conn = psycopg2.connect(
        host=_host,
        port=_port,
        database=_dbname,
        user=_user,
        password=_pw
    )
except psycopg2.DatabaseError as error:
    _conn = None
    print 'help'
    raise error


def connect():
    """Connect to DB"""
    global _conn
    try:
        _conn = psycopg2.connect(
            host=_host,
            port=_port,
            database=_dbname,
            user=_user,
            password=_pw
        )
    except psycopg2.DatabaseError as error:
        _conn = None
        raise error


def _execute(sql, data=None):
    """
    Execute an sql statement

    @param  sql:    sql statement
    @type   sql:    string
    @param  data:   data inserted into SQL statement
    @type   data:   tuple

    @return:    Cursor object
    @rtype:     psycopg2.extensions.cursor
    """
    # Set cursor
    if _open_cursor:
        cursor = _open_cursor
    else:
        cursor = _conn.cursor()
    # execute sql
    try:
        cursor.execute(sql, data)
        if not _open_cursor:
            _conn.commit()
    except psycopg2.DatabaseError:
        # Commit changes if not _open_cursor and no affected changes
        if not _open_cursor and cursor.rowcount == -1:
            _conn.commit()
        else:
            _conn.rollback()
        return None
    except psycopg2.InterfaceError as error:
        # Raise the error
        cursor.close()
        _conn.rollback()
        raise error
        return None

    return cursor


def execute(sql, data=None):
    """ Execute an update or insert statement with no return

    @param  sql:    sql statement
    @type   sql:    string
    @param  data:    data inserted into SQL statement
    @type   data:    tuple

    @return:    Boolean if no error was raised
    @rtype:     bool
    """
    cursor = _execute(sql, data)
    if _open_cursor:
        return True
    else:
        if cursor:
            cursor.close()
        return None
