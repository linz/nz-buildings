-- Revert nz-buildings:buildings_reference/update_suburb_locality_name_column from pg

BEGIN;

ALTER TABLE buildings_reference.suburb_locality
ADD COLUMN suburb_4th varchar(60),
ADD COLUMN suburb_3rd varchar(60),
ADD COLUMN suburb_2nd varchar(60),
ADD COLUMN suburb_1st varchar(60);

ALTER TABLE buildings_reference.suburb_locality
DROP COLUMN name;

COMMIT;
