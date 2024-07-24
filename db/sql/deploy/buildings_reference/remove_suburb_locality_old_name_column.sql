-- Deploy nz-buildings:buildings_reference/remove_suburb_locality_old_name_column to pg

BEGIN;

ALTER TABLE buildings_reference.suburb_locality
DROP COLUMN suburb_4th,
DROP COLUMN suburb_3rd,
DROP COLUMN suburb_2nd,
DROP COLUMN suburb_1st;

COMMIT;
