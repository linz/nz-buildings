-- Deploy nz-buildings:buildings/add-modified-date to pg

BEGIN;

ALTER TABLE buildings.building_outlines ADD last_modified timestamp;

COMMIT;
