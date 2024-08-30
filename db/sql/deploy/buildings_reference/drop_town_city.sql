-- Deploy nz-buildings:buildings_reference/drop_town_city_table to pg

BEGIN;

DROP TABLE buildings_reference.town_city;

ALTER TABLE buildings_reference.reference_update_log
DROP COLUMN town_city;

COMMIT;
