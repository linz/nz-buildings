====================
NZ Building Outlines
====================

.. image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg 
    :target: https://github.com/linz/nz-building-outlines/blob/master/LICENSE

Provides schemas and functions for the NZ Building Outlines system.

Installation
============

First install the project into the OS data share directory:

.. code-block:: shell

    sudo make install

Then you can load the schema into a target database:

.. code-block:: shell

    nz-buildings-load $DB_NAME

NOTE: the loader script will expect to find SQL scripts under /usr/share/nz-building-outlines/sql, if you want them found in a different directory you can set the BUILDINGSCHEMA_SQLDIR environment variable.

Upgrade
=======

The `nz-buildings-load` script will also upgrade as it currently replaces the existing schema. All data will be lost.

Testing
=======

Testing uses `pgTAP` via `pg_prove`.

.. code-block:: shell

    make check
