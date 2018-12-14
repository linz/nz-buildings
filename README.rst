============
NZ Buildings
============

.. image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg 
    :target: https://github.com/linz/nz-buildings/blob/master/LICENSE
    :alt: License

.. image:: https://api.travis-ci.com/linz/nz-buildings.svg?branch=master
    :target: https://travis-ci.com/linz/nz-buildings
    :alt: CI Status
    
.. image:: https://readthedocs.org/projects/nz-buildings/badge/?version=latest
    :target: https://nz-buildings.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
    
Provides schemas and functions for the NZ Building Outlines system.

Installation
============

First install the project into the OS data share directory:

.. code-block:: shell

    sudo make install

Then you can load the schema into a target database:

.. code-block:: shell

    nz-buildings-load $DB_NAME

NOTE: the loader script will expect to find SQL scripts under ``/usr/share/nz-buildings/sql``, if you want them found in a different directory you can set the ``BUILDINGSCHEMA_SQLDIR`` environment variable.

Upgrade
=======

The ``nz-buildings-load`` script will also upgrade as it currently replaces the existing schema. All data will be lost.

Testing
=======

Testing uses ``pgTAP`` via ``pg_prove``.

.. code-block:: shell

    make check
