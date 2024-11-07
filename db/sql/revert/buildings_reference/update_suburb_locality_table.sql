-- Revert nz-buildings:buildings_reference/update_suburb_locality_name_column from pg

BEGIN;

ALTER TABLE buildings_reference.suburb_locality
DROP COLUMN suburb_locality,
DROP COLUMN town_city;

COMMIT;
