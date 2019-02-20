==========
Change Log
==========

All notable changes to this project will be documented in this file.

Unreleased
==========

Added
-----

* Create a check dialog to list any duplicate ids found in added/related/matched table when publish button clicked during Bulk Load workflow

1.1.0
==========
19-02-2019

Added
-----

 * Topographic reference datasets can now be updated via LINZ Data Service changesets
 * Projection check for new capture source areas
 * bump_version command in makefile
 * Delete building outlines while in Alter Relationships workflow
 * Move to Next building outline while in Alter Relationships workflow
 * Ability to turn layers on and off easily based on their bulk load status during Bulk Load workflow
 * Create a check dialog to list any duplicate ids found in added/related/matched table when publish button clicked during Bulk Load workflow

Changed
-------

 * README rewritten to provide a more thorough overview of the system
 * Territorial Authority Grid is now a materialised view that can be automatically updated when Territorial Authority changes occur, not a table
 * Not removed button icon change and when pressed changes relationship table to select building in matched table

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
