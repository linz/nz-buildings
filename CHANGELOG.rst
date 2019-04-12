==========
Change Log
==========

All notable changes to this project will be documented in this file.

Unreleased
==========

* All up-to-date! :rocket:

Fixed
-----
* Compare new dataset with previous dataset INCLUDING removed outlines that have "not removed" flag.

1.3.0
==========
26-03-2019

Changed
-------

* Display the name and id together in the capture source combo box.

Fixed
-----

* Correctly populate capture source combo box when adding production outlines.

1.2.0
==========
13-03-2019

Added
-----

* Dialog that lists any duplicate ids found in added/related/matched table when publish button clicked during Bulk Load workflow
* Ability to update the suburb_locality, town_city, territorial_authority and territorial_authority_grid reference tables
* bulk_load_outlines and building_outlines admin boundary ids are updated along with the reference tables

Changed
-------

* IDs listed in colours that match their symbology in Alter Relationships workflow

Fixed
-----

* Allow multipolygons to be added as capture source areas
* Toggle editing on the correct layer when clicking reset button on new capture source area

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
