-- Deploy nz-buildings:buildings_reference/update_suburb_locality_name_column to pg

BEGIN;

ALTER TABLE buildings_reference.suburb_locality
ADD COLUMN name varchar(100);

UPDATE buildings_reference.suburb_locality
SET name = COALESCE(suburb_4th, suburb_3rd, suburb_2nd, suburb_1st);

ALTER TABLE buildings_reference.suburb_locality
ALTER COLUMN name SET NOT NULL;

ALTER TABLE buildings_reference.suburb_locality
DROP COLUMN suburb_4th,
DROP COLUMN suburb_3rd,
DROP COLUMN suburb_2nd,
DROP COLUMN suburb_1st;

COMMIT;
