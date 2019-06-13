==========
Change Log
==========

All notable changes to this project will be documented in this file.

Unreleased
==========

Added
-----

* Buildings toolbar and bulk load adding/editing functionality added to the alter relationships frame
* Update the error status and comment in the QA layer if bulk load outline edited (edit-geometry and delete-outline only)
* last_modified date column to buildings.building_outlines to track edits

Changed
-------

* Database migrations now managed by sqitch
* Database schema split into deploy/; revert/ and verify/ added
* Database test data is now stored in schema specific sql files
* Any edits made to the database outside of the code can be automatically added to/changed in the code using make dump_db_schema
* Changed editing functionality in bulk load to work through the buildings toolbar and use a popup dialog rather than be held in the frame
* Changed editing functionality in production to work through the buildings toolbar and use a popup dialog rather than be held in the frame
* Updated plugin editing functionality to allow the user to use the qgis split features tool and save the changes to the database
* Updated URL links
* last_modified date of buildings_lds tables are now the most recent of three columns (begin_lifespan, end_lifespan and last_modified) from buildings.building_outlines

Fixed
-----

* Warning messages for when multiple buildings are added at once
* Users can correctly remove added outlines or revert changes when adding multiple outlines with 'add outline' functionality.
* Remove functionality repopulate_error_attribute_table to LIQA plugin.

1.4.0
==========
10-05-2019

Changed
-------

* Removed building_outline_id from nz_building_outlines to make it clear that building_id is the persistent id.
* Account for UNIQUE constraints for data dictionary column parsing
* Updated metadata and data dictionary text and images in preparation for go-live.
* Published views of data adjusted based on user feedback.

Fixed
-----

* Compare new dataset with previous dataset INCLUDING removed outlines that have "not removed" flag.
* Use the current time as the begin_lifespan of building outlines when creating them rather than the date of bulk loading

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
