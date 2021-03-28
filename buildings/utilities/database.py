# -*- coding: utf-8 -*-
"""
################################################################################
#
# Copyright 2016 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the
# LICENSE file for more information.
#
################################################################################
"""
from __future__ import absolute_import
from builtins import str

import os
import psycopg2

from buildings.utilities.warnings import buildings_warning
from qgis.core import QgsDataSourceUri, QgsApplication

from . import config


config_path = os.path.join(QgsApplication.qgisSettingsDirPath(), "buildings", "pg_config.ini")

pg_config = config.read_config_file(config_path)
_host = pg_config["localhost"]["host"]
_port = pg_config["localhost"]["port"]
_dbname = pg_config["localhost"]["dbname"]
_user = pg_config["localhost"]["user"]
_pw = pg_config["localhost"]["password"]

_open_cursor = None

try:
    _conn = psycopg2.connect(host=_host, port=_port, database=_dbname, user=_user, password=_pw)
except psycopg2.DatabaseError as error:
    _conn = None
    buildings_warning("Database Error", str(error), "critical")


def rollback_open_cursor():
    """"""
    global _open_cursor
    if _open_cursor:
        _open_cursor.close()
        _open_cursor = None
        _conn.rollback()
        return 1


def commit_open_cursor():
    """"""
    global _open_cursor
    if _open_cursor:
        _open_cursor.close()
        _open_cursor = None
        _conn.commit()
        return 1


def connect():
    """Connect to DB"""
    global _conn
    try:
        _conn = psycopg2.connect(host=_host, port=_port, database=_dbname, user=_user, password=_pw)
    except psycopg2.DatabaseError as error:
        _conn = None
        buildings_warning("Database Error", str(error), "critical")

def write_to_txt(text):
    error_txt_path = os.path.join(QgsApplication.qgisSettingsDirPath(), "buildings", "errors.txt")

    file = open(error_txt_path,"a")
    file.write(text)
    file.close()


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
    except psycopg2.DatabaseError as error:
        # Commit changes if not _open_cursor and no affected changes
        if not _open_cursor and cursor.rowcount == -1:
            _conn.commit()
        else:
            _conn.rollback()
        txt = "db error \nsql {} \ndata {}".format(sql, data)
        write_to_txt(txt)
        buildings_warning("Database Error", str(error), "critical")

        return None
    except psycopg2.InterfaceError as error:
        # Raise the error
        cursor.close()
        _conn.rollback()
        buildings_warning("Interface Error", str(error), "critical")

        txt = "interface error \nsql {} \ndata {}".format(sql, data)
        write_to_txt(txt)

        return None

    return cursor


def execute_return(sql, data=None):
    cursor = _execute(sql, data)
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


def execute_no_commit(sql, data=None):
    cursor = _open_cursor
    try:
        _open_cursor.execute(sql, data)
    except psycopg2.DatabaseError as error:
        _conn.rollback()
        buildings_warning("Database Error", str(error), "critical")
        return None
    except psycopg2.InterfaceError as error:
        # Raise the error
        cursor.close()
        _conn.rollback()
        buildings_warning("Interface Error", str(error), "critical")
        return None

    return cursor


def open_cursor():
    """Open a cursor with a psycopg2 connection"""
    global _open_cursor
    _open_cursor = _conn.cursor()


def close_connection():
    _conn.close()


def close_cursor():
    global _open_cursor
    _open_cursor = None


def set_uri():
    """ Creates a QgsDataSourceUri with connection

    @return:    QGIS URI object
    @rtype:     qgis.core.QgsDataSourceUri
    """
    uri = QgsDataSourceUri()
    uri.setConnection(_host, _port, _dbname, _user, _pw)
    return uri
