==========
Change Log
==========

All notable changes to this project will be documented in this file.

Unreleased
==========

Added
-----

 * Topographic reference datasets can now be updated via LINZ Data Service changesets
 * Projection check for new capture source areas
 * bump_version command in makefile
 * README rewritten to provide a more thorough overview of the system

Fixed
-----

 * Buildings that overlapped by less than 5% were added to the related table in some scenarios

1.0.6
=====
17-01-2019

Added
-----

 * PostgreSQL / PostGIS schema definitions
 * QGIS data maintenance plugin
 * Automated documentation using sphinx / readthedocs
 * makefile and nz-buildings-load script for installation
 * Testing using pgTAP (database), unittest (plugin) with Travis-CI configuration
 * CHANGELOG, LICENSE
