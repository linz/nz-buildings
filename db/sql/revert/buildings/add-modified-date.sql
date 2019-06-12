-- Revert nz-buildings:buildings/add-modified-date from pg

BEGIN;

ALTER TABLE buildings.building_outlines DROP last_modified;

COMMIT;
