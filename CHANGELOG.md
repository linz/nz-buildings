# Changelog

All notable changes to this project will be documented in this file.


## Unreleased

### Changed
- The building outlines database now holds its own imagery survey index
- Modified date column in LDS dataset views takes into account name or use changes
- Data dictionary and metadata updated to reflect additional Tasman, Nelson, Otago and Dunedin building outlines updates

### Fixed
- Added the supplied_dataset_id and a new primary key to the buildings_bulk_load.removed table to allow a building to be identified for removal more than once
- Fixed PostgreSQL installation for continuous integration
- Outlines split in production now cause all split outputs to have new identifiers
- Edit dialog doesn't use the error dialog to avoid problem of hidden dialogs


## 3.5.0
2020-05-29

### Changed
- Completed upgrade to QGIS 3.10
- Some symbology changed to enable the removal of QgsHighlight due to bugs

### Fixed
- Outlines deleted or split in production are now added to all_sources table


## 3.4.0
2020-04-08

### Added
- Users are now able to split features in Production

### Changed
- `make check` uses built installer, not system installer

### Fixed
- Errors that occur during `make check` are better exposed to the user
- Exit build process immediately if `sqitch` not found


## 3.3.0
2020-04-01

### Added
- QGIS plugin now deploys to LINZ QGIS Plugin Repository automatically on version tag
- Metadata links to ArcGIS Online dataset mirror / ArcGIS REST Services

### Changed
- CI now runs on pull request (to help contribute from forks)


## 3.2.0
2020-03-02

### Added
- Dependabot enabled to manage Python dependencies.
- New data dictionary section defining how suburbs and localities are determined.

### Changed
- Metadata updated to reflect additional Gisborne outlines.
- Optimised the process of updating suburbs and localities.
- Islands that have an empty suburb_4th column can now be assigned to a building using suburb_3rd.
- Replaced Travis CI with Github Actions for continuous integration.

### Fixed
- Only reference suburbs and localities that are of types: ISLAND, LOCALITY, PARK_RESERVE, SUBURB.
- Corrected a join for territorial authority updates.
- Apply the NZ Imagery Surveys reference table update to NZ Imagery Survey Index to the correct files.


## 3.1.0
2020-01-15

### Added
- Ensure git commit messages conform to the conventional commits spec
- Circular buildings smaller than 16sqm are removed on bulk load

### Changed
- Updated NZ Imagery Surveys reference table to NZ Imagery Survey Index
- Metadata updated to reflect additional Bay of Plenty outlines.

### Fixed
- Bulk load outlines and alter relationships edit vertices and split features bug


## 3.0.0
2019-12-06

### Changed
- Updated buildings plugin from QGIS2 to QGIS3

### Fixed
- Include name in the update or insert functions for reference data (hut, shelter, bivouac and protected area).
- Fix sqitch deployment to 'sqitch deploy --verify'


## 2.0.0
2019-08-02

### Added
- Buildings toolbar and bulk load adding/editing functionality added to the alter relationships frame
- Update the error status and comment in the QA layer if bulk load outline edited (edit-geometry and delete-outline only)
- last_modified date column to buildings.building_outlines to track edits
- Database and Plugin test data can be updated using the makefile command 'make dump_schema'
- Added huts, shelters, bivouacs, and protected areas to the buildings reference schema

### Changed
- Database migrations now managed by sqitch
- Database schema split into deploy/; revert/ and verify/ added
- Database test data is now stored in schema specific sql files
- Any edits made to the database outside of the code can be automatically added to/changed in the code using make dump_db_schema
- Changed editing functionality in bulk load to work through the buildings toolbar and use a popup dialog rather than be held in the frame
- Changed editing functionality in production to work through the buildings toolbar and use a popup dialog rather than be held in the frame
- Updated plugin editing functionality to allow the user to use the qgis split features tool and save the changes to the database
- Updated URL links
- last_modified date of buildings_lds tables are now the most recent of three columns (begin_lifespan, end_lifespan and last_modified) from buildings.building_outlines
- Plugin test data is now stored in schema specific sql files

### Fixed
- Warning messages for when multiple buildings are added at once
- Users can correctly remove added outlines or revert changes when adding multiple outlines with 'add outline' functionality.
- Remove functionality repopulate_error_attribute_table to LIQA plugin.
- Add dist:Trusty in travis-ci config so travis-ci can run in the right build.


## 1.4.0
2019-05-10

### Changed
- Removed building_outline_id from nz_building_outlines to make it clear that building_id is the persistent id.
- Account for UNIQUE constraints for data dictionary column parsing
- Updated metadata and data dictionary text and images in preparation for go-live.
- Published views of data adjusted based on user feedback.

### Fixed
- Compare new dataset with previous dataset INCLUDING removed outlines that have "not removed" flag.
- Use the current time as the begin_lifespan of building outlines when creating them rather than the date of bulk loading


## 1.3.0
2019-03-26

### Changed
- Display the name and id together in the capture source combo box.

### Fixed
- Correctly populate capture source combo box when adding production outlines.


## 1.2.0
2019-03-13

### Added
- Dialog that lists any duplicate ids found in added/related/matched table when publish button clicked during Bulk Load workflow
- Ability to update the suburb_locality, town_city, territorial_authority and territorial_authority_grid reference tables
- bulk_load_outlines and building_outlines admin boundary ids are updated along with the reference tables

### Changed
- IDs listed in colours that match their symbology in Alter Relationships workflow

### Fixed
- Allow multipolygons to be added as capture source areas
- Toggle editing on the correct layer when clicking reset button on new capture source area


## 1.1.0
2019-02-19

### Added
- Topographic reference datasets can now be updated via LINZ Data Service changesets
- Projection check for new capture source areas
- bump_version command in makefile
- Delete building outlines while in Alter Relationships workflow
- Move to Next building outline while in Alter Relationships workflow
- Ability to turn layers on and off easily based on their bulk load status during Bulk Load workflow
- Create a check dialog to list any duplicate ids found in added/related/matched table when publish button clicked during Bulk Load workflow

### Changed
- README rewritten to provide a more thorough overview of the system
- Territorial Authority Grid is now a materialised view that can be automatically updated when Territorial Authority changes occur, not a table
- Not removed button icon change and when pressed changes relationship table to select building in matched table

### Fixed
- Buildings that overlapped by less than 5% were added to the related table in some scenarios


## 1.0.6
2019-01-17

### Added
- PostgreSQL / PostGIS schema definitions
- QGIS data maintenance plugin
- Automated documentation using sphinx / readthedocs
- makefile and nz-buildings-load script for installation
- Testing using pgTAP (database), unittest (plugin) with Travis-CI configuration
- CHANGELOG, LICENSE
